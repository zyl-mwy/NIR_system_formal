#include <QObject>
#include <QDebug>
#include <QCoreApplication>
#include <QDir>
#include <QFileInfo>
#include <vector>
#include <memory>

#include "spectrum_predictor_interface.h"
#include <onnxruntime/onnxruntime_cxx_api.h>

// ONNX 预测器类（随机森林算法版本，固定1024输入）
class OnnxSpectrumPredictor {
public:
    OnnxSpectrumPredictor() : modelLoaded_(false) {}
    
    bool loadModel(const std::string& model_path) {
        try {
            // 初始化 ONNX Runtime 环境
            env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "RFPredictor");
            
            // 创建会话选项
            Ort::SessionOptions session_options;
            session_options.SetIntraOpNumThreads(1);
            
            // 创建会话（加载模型）
            session_ = std::make_unique<Ort::Session>(*env_, model_path.c_str(), session_options);
            
            // 获取输入输出信息
            Ort::AllocatorWithDefaultOptions allocator;
            
            // 输入信息
            size_t num_input_nodes = session_->GetInputCount();
            input_names_.resize(num_input_nodes);
            
            for (size_t i = 0; i < num_input_nodes; i++) {
                auto input_name = session_->GetInputNameAllocated(i, allocator);
                input_names_[i] = input_name.get();
            }
            
            // 输出信息
            size_t num_output_nodes = session_->GetOutputCount();
            output_names_.resize(num_output_nodes);
            
            for (size_t i = 0; i < num_output_nodes; i++) {
                auto output_name = session_->GetOutputNameAllocated(i, allocator);
                output_names_[i] = output_name.get();
            }
            
            modelLoaded_ = true;
            return true;
        } catch (const std::exception& e) {
            qWarning() << "加载模型失败:" << e.what();
            modelLoaded_ = false;
            return false;
        }
    }
    
    float predict(const std::vector<float>& spectrum_data) {
        if (!modelLoaded_ || spectrum_data.size() != 1024) {
            throw std::invalid_argument("模型未加载或数据长度不正确");
        }
        
        // 准备输入数据
        std::vector<int64_t> input_shape = {1, 1024};
        std::vector<float> input_values = spectrum_data;
        
        // 创建输入张量
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault);
        
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info, input_values.data(), input_values.size(),
            input_shape.data(), input_shape.size());
        
        // 准备输入输出名称
        std::vector<const char*> input_node_names;
        for (const auto& name : input_names_) {
            input_node_names.push_back(name.c_str());
        }
        
        std::vector<const char*> output_node_names;
        for (const auto& name : output_names_) {
            output_node_names.push_back(name.c_str());
        }
        
        // 运行推理
        auto output_tensors = session_->Run(
            Ort::RunOptions{nullptr},
            input_node_names.data(), &input_tensor, 1,
            output_node_names.data(), 1);
        
        // 获取输出结果
        float* float_array = output_tensors.front().GetTensorMutableData<float>();
        return float_array[0];
    }
    
    bool isModelLoaded() const {
        return modelLoaded_;
    }

private:
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    std::vector<std::string> input_names_;
    std::vector<std::string> output_names_;
    bool modelLoaded_;
};

// 随机森林预测插件
class RFPredictorPlugin : public QObject, public SpectrumPredictorPlugin {
  Q_OBJECT
  Q_PLUGIN_METADATA(IID SpectrumPredictorPlugin_iid)
  Q_INTERFACES(SpectrumPredictorPlugin)

 public:
  RFPredictorPlugin() : predictor_(std::make_unique<OnnxSpectrumPredictor>()) {}
  
  QString name() const override { 
    return QStringLiteral("随机森林预测器 (Random Forest)"); 
  }
  
  QString algorithm() const override {
    return QStringLiteral("random_forest");
  }
  
  QString getDefaultModelPath() const override {
    // 权重文件路径构建逻辑在插件中实现
    QString folderName = QStringLiteral("rf_predictor");
    QString appDir = QCoreApplication::applicationDirPath();
    
    // 构建完整路径: 从应用程序目录向上查找 predictor_train 文件夹
    // 应用程序可能在 build/ 目录中，需要向上查找项目根目录
    QDir appDirObj(appDir);
    
    // 尝试向上查找 predictor_train 文件夹（最多向上3级）
    for (int i = 0; i < 3; i++) {
      QString testPath = appDirObj.absoluteFilePath(
        QString("predictor_train/%1/spectrum_model.onnx").arg(folderName)
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
      QString("predictor_train/%1/spectrum_model.onnx").arg(folderName)
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
    if (spectrumData.size() != 1024) {
      qWarning() << "光谱数据长度不正确，期望1024，实际:" << spectrumData.size();
      return 0.0;
    }
    
    // 转换为 std::vector<float>
    std::vector<float> data;
    data.reserve(1024);
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
  std::unique_ptr<OnnxSpectrumPredictor> predictor_;
};

#include "rf_predictor_plugin.moc"

