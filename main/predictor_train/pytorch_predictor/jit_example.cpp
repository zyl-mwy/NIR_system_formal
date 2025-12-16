/*
 * PyTorch JIT C++ 示例代码
 * 演示如何在 C++ 中使用 libtorch 加载和运行 Python 导出的 JIT 模型
 * 
 * 编译方法:
 *   使用 CMake (推荐):
 *   mkdir build && cd build
 *   cmake ..
 *   make
 *   ./jit_example ../spectrum_model.jit
 */

#include <iostream>
#include <vector>
#include <memory>
#include <cassert>
#include <cstdlib>
#include <ctime>

// libtorch 头文件
#include <torch/script.h>
#include <torch/torch.h>

class JitSpectrumPredictor {
public:
    JitSpectrumPredictor(const std::string& model_path) {
        try {
            // 加载 JIT 模型
            std::cout << "正在加载模型: " << model_path << std::endl;
            model_ = torch::jit::load(model_path);
            model_.eval();
            
            std::cout << "模型加载成功！" << std::endl;
            
            // 打印输入输出信息（格式与 ONNX 版本一致）
            printModelInfo();
            
        } catch (const std::exception& e) {
            std::cerr << "加载模型失败: " << e.what() << std::endl;
            throw;
        }
    }
    
    void printModelInfo() {
        // 格式与 ONNX 版本一致
        std::cout << "输入 0 名称: input" << std::endl;
        std::cout << "输入 0 形状: [1, 1024]" << std::endl;
        std::cout << "输出 0 名称: output" << std::endl;
        std::cout << "输出 0 形状: [1]" << std::endl;
    }
    
    // 预测函数：输入1024个光谱数据点，返回预测值
    float predict(const std::vector<float>& spectrum_data) {
        if (spectrum_data.size() != 1024) {
            throw std::invalid_argument("光谱数据必须包含1024个数据点");
        }
        
        try {
            // 创建输入张量 (1, 1024)
            torch::Tensor input_tensor = torch::from_blob(
                const_cast<float*>(spectrum_data.data()),
                {1, 1024},
                torch::kFloat32
            );
            
            // 准备输入
            std::vector<torch::jit::IValue> inputs;
            inputs.push_back(input_tensor);
            
            // 运行推理（禁用梯度计算）
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
            std::cerr << "预测失败: " << e.what() << std::endl;
            throw;
        }
    }
    
    // 批量预测
    std::vector<float> predictBatch(const std::vector<std::vector<float>>& spectra) {
        if (spectra.empty()) {
            return {};
        }
        
        size_t batch_size = spectra.size();
        
        // 将多个光谱数据展平为一个数组
        std::vector<float> input_values;
        input_values.reserve(batch_size * 1024);
        for (const auto& spectrum : spectra) {
            if (spectrum.size() != 1024) {
                throw std::invalid_argument("每个光谱数据必须包含1024个数据点");
            }
            input_values.insert(input_values.end(), spectrum.begin(), spectrum.end());
        }
        
        // 创建输入张量 [batch_size, 1024]
        torch::Tensor input_tensor = torch::from_blob(
            input_values.data(),
            {static_cast<long>(batch_size), 1024},
            torch::kFloat32
        );
        
        // 准备输入
        std::vector<torch::jit::IValue> inputs;
        inputs.push_back(input_tensor);
        
        // 运行推理（禁用梯度计算）
        torch::NoGradGuard no_grad;
        auto output = model_.forward(inputs);
        
        // 获取输出结果
        std::vector<float> predictions;
        if (output.isTensor()) {
            auto output_tensor = output.toTensor();
            // 确保输出是1D或2D张量
            if (output_tensor.dim() == 0) {
                // 标量，只有一个预测值
                predictions.push_back(output_tensor.item<float>());
            } else if (output_tensor.dim() == 1) {
                // 1D张量 [batch_size]
                auto accessor = output_tensor.accessor<float, 1>();
                for (size_t i = 0; i < batch_size; i++) {
                    predictions.push_back(accessor[i]);
                }
            } else if (output_tensor.dim() == 2 && static_cast<size_t>(output_tensor.size(0)) == batch_size) {
                // 2D张量 [batch_size, 1]
                auto accessor = output_tensor.accessor<float, 2>();
                for (size_t i = 0; i < batch_size; i++) {
                    predictions.push_back(accessor[i][0]);
                }
            } else {
                // 展平并取前 batch_size 个值
                auto flattened = output_tensor.flatten();
                auto accessor = flattened.accessor<float, 1>();
                for (size_t i = 0; i < batch_size && i < static_cast<size_t>(flattened.size(0)); i++) {
                    predictions.push_back(accessor[i]);
                }
            }
        } else if (output.isScalar()) {
            // 标量输出，只有一个预测值
            predictions.push_back(output.toScalar().toFloat());
        } else {
            throw std::runtime_error("无法解析模型输出");
        }
        
        return predictions;
    }

private:
    torch::jit::script::Module model_;
};


// 示例使用
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "用法: " << argv[0] << " <jit_model_path>" << std::endl;
        std::cerr << "示例: " << argv[0] << " spectrum_model.jit" << std::endl;
        return 1;
    }
    
    std::string model_path = argv[1];
    
    try {
        // 创建预测器
        JitSpectrumPredictor predictor(model_path);
        std::cout << std::endl;
        
        // 创建测试数据（1024个随机值，模拟光谱数据）
        // 使用 rand() 与 ONNX 版本保持一致
        std::vector<float> test_spectrum(1024);
        for (size_t i = 0; i < 1024; i++) {
            test_spectrum[i] = static_cast<float>(rand()) / RAND_MAX * 10000.0f;
        }
        
        // 单样本预测
        std::cout << "执行单样本预测..." << std::endl;
        float prediction = predictor.predict(test_spectrum);
        std::cout << "预测值: " << prediction << std::endl << std::endl;
        
        // 批量预测
        std::cout << "执行批量预测..." << std::endl;
        std::vector<std::vector<float>> batch_spectra(3);
        for (size_t i = 0; i < 3; i++) {
            batch_spectra[i].resize(1024);
            for (size_t j = 0; j < 1024; j++) {
                batch_spectra[i][j] = static_cast<float>(rand()) / RAND_MAX * 10000.0f;
            }
        }
        
        std::vector<float> batch_predictions = predictor.predictBatch(batch_spectra);
        std::cout << "批量预测结果:" << std::endl;
        for (size_t i = 0; i < batch_predictions.size(); i++) {
            std::cout << "  样本 " << i << ": " << batch_predictions[i] << std::endl;
        }
        
    } catch (const std::exception& e) {
        std::cerr << "错误: " << e.what() << std::endl;
        return 1;
    }
    
    return 0;
}
