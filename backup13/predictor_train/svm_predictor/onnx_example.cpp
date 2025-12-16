/*
 * ONNX Runtime C++ 示例代码
 * 演示如何在 C++ 中使用 ONNX Runtime 加载和运行 Python 导出的模型
 * 
 * 编译方法:
 *   g++ -std=c++17 onnx_data_example.cpp -lonnxruntime -o onnx_data_example
 * 
 * 或者使用 CMake (推荐):
 *   在 CMakeLists.txt 中添加:
 *   find_package(onnxruntime REQUIRED)
 *   target_link_libraries(your_target onnxruntime::onnxruntime)
 */

#include <iostream>
#include <vector>
#include <memory>
#include <cassert>

// ONNX Runtime 头文件
#include <onnxruntime/onnxruntime_cxx_api.h>

class OnnxSpectrumPredictor {
public:
    OnnxSpectrumPredictor(const std::string& model_path) {
        // 初始化 ONNX Runtime 环境
        env_ = std::make_unique<Ort::Env>(ORT_LOGGING_LEVEL_WARNING, "SpectrumPredictor");
        
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
        input_shapes_.resize(num_input_nodes);
        
        for (size_t i = 0; i < num_input_nodes; i++) {
            auto input_name = session_->GetInputNameAllocated(i, allocator);
            input_names_[i] = input_name.get();
            
            Ort::TypeInfo input_type_info = session_->GetInputTypeInfo(i);
            auto input_tensor_info = input_type_info.GetTensorTypeAndShapeInfo();
            auto input_dims = input_tensor_info.GetShape();
            input_shapes_[i] = input_dims;
            
            std::cout << "输入 " << i << " 名称: " << input_names_[i] << std::endl;
            std::cout << "输入 " << i << " 形状: [";
            for (size_t j = 0; j < input_dims.size(); j++) {
                std::cout << input_dims[j];
                if (j < input_dims.size() - 1) std::cout << ", ";
            }
            std::cout << "]" << std::endl;
        }
        
        // 输出信息
        size_t num_output_nodes = session_->GetOutputCount();
        output_names_.resize(num_output_nodes);
        
        for (size_t i = 0; i < num_output_nodes; i++) {
            auto output_name = session_->GetOutputNameAllocated(i, allocator);
            output_names_[i] = output_name.get();
            
            Ort::TypeInfo output_type_info = session_->GetOutputTypeInfo(i);
            auto output_tensor_info = output_type_info.GetTensorTypeAndShapeInfo();
            auto output_dims = output_tensor_info.GetShape();
            
            std::cout << "输出 " << i << " 名称: " << output_names_[i] << std::endl;
            std::cout << "输出 " << i << " 形状: [";
            for (size_t j = 0; j < output_dims.size(); j++) {
                std::cout << output_dims[j];
                if (j < output_dims.size() - 1) std::cout << ", ";
            }
            std::cout << "]" << std::endl;
        }
        
        // 获取输入大小（核心算法改动：动态检测）
        if (!input_shapes_.empty() && !input_shapes_[0].empty()) {
            input_size_ = input_shapes_[0].back();
            if (input_size_ < 0) {
                input_size_ = 1024;  // 默认值
            }
        } else {
            input_size_ = 1024;  // 默认值
        }
    }
    
    // 预测函数：输入光谱数据点，返回预测值
    float predict(const std::vector<float>& spectrum_data) {
        if (spectrum_data.size() != input_size_) {
            throw std::invalid_argument("光谱数据必须包含" + std::to_string(input_size_) + "个数据点");
        }
        
        // 准备输入数据
        std::vector<int64_t> input_shape = {1, static_cast<int64_t>(input_size_)};
        std::vector<float> input_values = spectrum_data;
        
        // 创建输入张量
        Ort::MemoryInfo memory_info = Ort::MemoryInfo::CreateCpu(
            OrtArenaAllocator, OrtMemTypeDefault);
        
        Ort::Value input_tensor = Ort::Value::CreateTensor<float>(
            memory_info, input_values.data(), input_values.size(),
            input_shape.data(), input_shape.size());
        
        // 准备输入名称（转换为 char*）
        std::vector<const char*> input_node_names;
        for (const auto& name : input_names_) {
            input_node_names.push_back(name.c_str());
        }
        
        // 准备输出名称
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
        float prediction = float_array[0];
        
        return prediction;
    }
    
    // 批量预测
    std::vector<float> predictBatch(const std::vector<std::vector<float>>& spectra) {
        if (spectra.empty()) {
            return {};
        }
        
        size_t batch_size = spectra.size();
        std::vector<int64_t> input_shape = {static_cast<int64_t>(batch_size), static_cast<int64_t>(input_size_)};
        
        // 将多个光谱数据展平为一个数组（核心算法改动：动态检测）
        std::vector<float> input_values;
        input_values.reserve(batch_size * input_size_);
        for (const auto& spectrum : spectra) {
            if (spectrum.size() != input_size_) {
                throw std::invalid_argument("每个光谱数据必须包含" + std::to_string(input_size_) + "个数据点");
            }
            input_values.insert(input_values.end(), spectrum.begin(), spectrum.end());
        }
        
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
        std::vector<float> predictions(float_array, float_array + batch_size);
        
        return predictions;
    }

    // 获取输入大小
    size_t getInputSize() const {
        return input_size_;
    }

private:
    std::unique_ptr<Ort::Env> env_;
    std::unique_ptr<Ort::Session> session_;
    std::vector<std::string> input_names_;
    std::vector<std::string> output_names_;
    std::vector<std::vector<int64_t>> input_shapes_;
    size_t input_size_;
};


// 示例使用
int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "用法: " << argv[0] << " <onnx_model_path>" << std::endl;
        std::cerr << "示例: " << argv[0] << " model.onnx" << std::endl;
        return 1;
    }
    
    std::string model_path = argv[1];
    
    try {
        // 创建预测器
        std::cout << "正在加载 ONNX 模型: " << model_path << std::endl;
        OnnxSpectrumPredictor predictor(model_path);
        std::cout << "模型加载成功！" << std::endl << std::endl;
        
        // 获取输入大小（核心算法改动：动态检测）
        size_t input_size = predictor.getInputSize();
        
        // 创建测试数据（随机值，模拟光谱数据）
        std::vector<float> test_spectrum(input_size);
        for (size_t i = 0; i < input_size; i++) {
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
            batch_spectra[i].resize(input_size);
            for (size_t j = 0; j < input_size; j++) {
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

