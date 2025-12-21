#include <QObject>
#include <QDebug>
#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <vector>
#include <memory>

#include "spectrum_predictor_interface.h"

// Qt 的 slots 宏与 libtorch 的 slots() 方法冲突，需要先取消定义
#ifdef slots
#undef slots
#endif

#include <torch/script.h>
#include <torch/torch.h>

// 如果需要，可以重新定义 slots 宏（但通常不需要）
// #define slots

// PyTorch 预测器类（使用 libtorch，固定1024输入）
class LibTorchSpectrumPredictor {
public:
    LibTorchSpectrumPredictor() : modelLoaded_(false), input_size_(1024) {}
    
    bool loadModel(const std::string& model_path) {
        try {
            // 加载 JIT 模型
            model_ = torch::jit::load(model_path);
            model_.eval();
            
            modelLoaded_ = true;
            qDebug() << "PyTorch 模型加载成功:" << model_path.c_str();
            return true;
        } catch (const std::exception& e) {
            qWarning() << "加载 PyTorch 模型失败:" << e.what();
            modelLoaded_ = false;
            return false;
        }
    }
    
    float predict(const std::vector<float>& spectrum_data) {
        if (!modelLoaded_) {
            throw std::invalid_argument("模型未加载");
        }
        
        if (spectrum_data.size() != static_cast<size_t>(input_size_)) {
            throw std::invalid_argument("数据长度不正确，期望" + std::to_string(input_size_) + 
                                       "，实际" + std::to_string(spectrum_data.size()));
        }
        
        try {
            // 创建输入张量 (1, 1024)
            std::vector<torch::jit::IValue> inputs;
            torch::Tensor input_tensor = torch::from_blob(
                const_cast<float*>(spectrum_data.data()),
                {1, static_cast<int64_t>(input_size_)},
                torch::kFloat32
            );
            
            inputs.push_back(input_tensor);
            
            // 运行推理
            torch::NoGradGuard no_grad;
            auto output = model_.forward(inputs);
            
            // 获取输出值
            float result = 0.0f;
            if (output.isTensor()) {
                auto output_tensor = output.toTensor();
                result = output_tensor.item<float>();
            } else if (output.isScalar()) {
                result = output.toScalar().toFloat();
            } else {
                throw std::runtime_error("无法解析模型输出");
            }
            
            return result;
        } catch (const std::exception& e) {
            qWarning() << "PyTorch 预测失败:" << e.what();
            throw;
        }
    }
    
    bool isModelLoaded() const {
        return modelLoaded_;
    }
    
    size_t getInputSize() const {
        return input_size_;
    }

private:
    torch::jit::script::Module model_;
    bool modelLoaded_;
    size_t input_size_;
};

// PyTorch 预测插件
class PyTorchPredictorPlugin : public QObject, public SpectrumPredictorPlugin {
  Q_OBJECT
  Q_PLUGIN_METADATA(IID SpectrumPredictorPlugin_iid)
  Q_INTERFACES(SpectrumPredictorPlugin)

 public:
  PyTorchPredictorPlugin() : predictor_(std::make_unique<LibTorchSpectrumPredictor>()) {}
  
  QString name() const override { 
    return QStringLiteral("PyTorch 神经网络预测器"); 
  }
  
  QString algorithm() const override {
    return QStringLiteral("pytorch");
  }
  
  QString getDefaultModelPath() const override {
    // 权重文件路径构建逻辑在插件中实现
    QString folderName = QStringLiteral("pytorch_predictor");
    QString appDir = QCoreApplication::applicationDirPath();
    
    // 构建完整路径: 从应用程序目录向上查找 predictor_train 文件夹
    // 应用程序可能在 build/ 目录中，需要向上查找项目根目录
    QDir appDirObj(appDir);
    
    // 尝试向上查找 predictor_train 文件夹（最多向上3级）
    for (int i = 0; i < 3; i++) {
      QString testPath = appDirObj.absoluteFilePath(
        QString("predictor_train/%1/spectrum_model.jit").arg(folderName)
      );
      QFileInfo fileInfo(testPath);
      if (fileInfo.exists() && fileInfo.isFile()) {
        qDebug() << "找到模型文件:" << testPath;
        return testPath;
      }
      
      // 如果不在项目根目录，向上查找
      if (!appDirObj.cdUp()) {
        break;
      }
    }
    
    // 如果找不到，返回相对路径（假设在项目根目录）
    QString modelPath = appDirObj.absoluteFilePath(
      QString("predictor_train/%1/spectrum_model.jit").arg(folderName)
    );
    
    qWarning() << "模型文件可能不存在，返回路径:" << modelPath;
    return modelPath;
  }
  
  bool loadModel(const QString &modelPath) override {
    if (modelPath.isEmpty()) {
      return false;
    }
    return predictor_->loadModel(modelPath.toStdString());
  }
  
  double predict(const QVariantList &spectrumData) override {
    size_t expectedSize = predictor_->getInputSize();
    if (spectrumData.size() != static_cast<int>(expectedSize)) {
      qWarning() << "光谱数据长度不正确，期望" << expectedSize << "，实际:" << spectrumData.size();
      return 0.0;
    }
    
    // 转换为 std::vector<float>
    std::vector<float> data;
    data.reserve(expectedSize);
    for (const QVariant &v : spectrumData) {
      data.push_back(static_cast<float>(v.toDouble()));
    }
    
    try {
      return static_cast<double>(predictor_->predict(data));
    } catch (const std::exception& e) {
      qWarning() << "预测失败:" << e.what();
      return 0.0;
    }
  }
  
  bool isModelLoaded() const override {
    return predictor_->isModelLoaded();
  }

 private:
  std::unique_ptr<LibTorchSpectrumPredictor> predictor_;
};

#include "pytorch_predictor_plugin.moc"

