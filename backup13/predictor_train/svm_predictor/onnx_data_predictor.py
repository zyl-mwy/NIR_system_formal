#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONNX Runtime Python 示例代码
演示如何在 Python 中使用 ONNX Runtime 加载和运行 ONNX 模型
功能与 onnx_data_example.cpp 相同
"""

import numpy as np
import sys
import argparse
from typing import List, Union, Optional

try:
    import onnxruntime as ort
    ONNX_RUNTIME_AVAILABLE = True
except ImportError:
    ONNX_RUNTIME_AVAILABLE = False
    print("错误: onnxruntime 未安装，请运行: pip install onnxruntime")


class OnnxSpectrumPredictor:
    """ONNX 光谱数据预测器（Python 版本）"""
    
    def __init__(self, model_path: str):
        """
        初始化预测器
        
        Args:
            model_path: ONNX 模型文件路径
        """
        if not ONNX_RUNTIME_AVAILABLE:
            raise ImportError("onnxruntime 未安装，请运行: pip install onnxruntime")
        
        # 创建 ONNX Runtime 会话
        self.session = ort.InferenceSession(model_path)
        
        # 获取输入输出信息（格式与 C++ 版本一致）
        num_input_nodes = len(self.session.get_inputs())
        num_output_nodes = len(self.session.get_outputs())
        
        self.input_names_ = []
        self.output_names_ = []
        
        # 输入信息
        for i in range(num_input_nodes):
            input_info = self.session.get_inputs()[i]
            input_name = input_info.name
            input_shape = input_info.shape
            self.input_names_.append(input_name)
            
            # 格式化为与 C++ 一致的输出
            shape_str = "["
            for j, dim in enumerate(input_shape):
                if dim is None or dim == -1:
                    shape_str += "-1"
                else:
                    shape_str += str(dim)
                if j < len(input_shape) - 1:
                    shape_str += ", "
            shape_str += "]"
            
            print(f"输入 {i} 名称: {input_name}")
            print(f"输入 {i} 形状: {shape_str}")
        
        # 输出信息
        for i in range(num_output_nodes):
            output_info = self.session.get_outputs()[i]
            output_name = output_info.name
            output_shape = output_info.shape
            self.output_names_.append(output_name)
            
            # 格式化为与 C++ 一致的输出
            shape_str = "["
            for j, dim in enumerate(output_shape):
                if dim is None or dim == -1:
                    shape_str += "-1"
                else:
                    shape_str += str(dim)
                if j < len(output_shape) - 1:
                    shape_str += ", "
            shape_str += "]"
            
            print(f"输出 {i} 名称: {output_name}")
            print(f"输出 {i} 形状: {shape_str}")
        
        # 保存第一个输入输出名称（用于兼容性）
        self.input_name = self.input_names_[0]
        self.output_name = self.output_names_[0]
        
        # 获取输入维度（动态检测 - 核心算法改动）
        input_shape = self.session.get_inputs()[0].shape
        if len(input_shape) >= 2:
            self.input_size = input_shape[-1] if input_shape[-1] is not None and input_shape[-1] > 0 else 512
        else:
            self.input_size = 512  # 默认值
    
    def predict(self, spectrum_data: Union[List[float], np.ndarray]) -> float:
        """
        单样本预测：输入光谱数据点，返回预测值
        
        Args:
            spectrum_data: 光谱数据，必须包含指定数量的数据点
            
        Returns:
            预测值
        """
        # 转换为 numpy 数组
        if isinstance(spectrum_data, list):
            spectrum_data = np.array(spectrum_data, dtype=np.float32)
        else:
            spectrum_data = spectrum_data.astype(np.float32)
        
        # 检查数据长度（核心算法改动：动态检测）
        if spectrum_data.size != self.input_size:
            raise ValueError(f"光谱数据必须包含{self.input_size}个数据点，当前: {spectrum_data.size}")
        
        # 确保是2D数组 [1, input_size]
        if spectrum_data.ndim == 1:
            spectrum_data = spectrum_data.reshape(1, -1)
        
        # 运行推理
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: spectrum_data}
        )
        
        # 获取预测值（修复 DeprecationWarning）
        prediction_value = outputs[0][0]
        if isinstance(prediction_value, np.ndarray):
            prediction = float(prediction_value.item())
        else:
            prediction = float(prediction_value)
        return prediction
    
    def predict_batch(self, spectra: List[Union[List[float], np.ndarray]]) -> List[float]:
        """
        批量预测：输入多个光谱数据，返回预测值列表
        
        Args:
            spectra: 光谱数据列表，每个光谱数据必须包含指定数量的数据点
            
        Returns:
            预测值列表
        """
        if not spectra:
            return []
        
        batch_size = len(spectra)
        
        # 转换为 numpy 数组并检查（核心算法改动：动态检测）
        batch_data = []
        for i, spectrum in enumerate(spectra):
            if isinstance(spectrum, list):
                spectrum = np.array(spectrum, dtype=np.float32)
            else:
                spectrum = spectrum.astype(np.float32)
            
            if spectrum.size != self.input_size:
                raise ValueError(f"第 {i} 个光谱数据必须包含{self.input_size}个数据点，当前: {spectrum.size}")
            
            if spectrum.ndim == 1:
                spectrum = spectrum.reshape(1, -1)
            
            batch_data.append(spectrum)
        
        # 合并为批次 [batch_size, input_size]
        batch_array = np.vstack(batch_data)
        
        # 运行推理
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: batch_array}
        )
        
        # 获取预测值列表
        predictions = [float(p) for p in outputs[0].flatten()]
        return predictions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='ONNX Runtime Python 预测程序 - 使用 ONNX 模型进行光谱数据预测',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本使用
  python3 onnx_predictor.py spectrum_model.onnx
  
  # 使用自定义测试数据
  python3 onnx_predictor.py spectrum_model.onnx --test-data-file data.csv
  
  # 批量预测
  python3 onnx_predictor.py spectrum_model.onnx --batch-size 10
        """
    )
    
    parser.add_argument(
        'model_path',
        type=str,
        help='ONNX 模型文件路径'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='批量预测的样本数量（默认: 3，与 C++ 版本一致）'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='随机种子（用于生成测试数据，默认: 不设置，与 C++ 版本一致）'
    )
    
    parser.add_argument(
        '--single-only',
        action='store_true',
        help='只执行单样本预测（不执行批量预测）'
    )
    
    args = parser.parse_args()
    
    if not ONNX_RUNTIME_AVAILABLE:
        print("错误: onnxruntime 未安装")
        print("请运行: pip install onnxruntime")
        sys.exit(1)
    
    try:
        # 创建预测器（输出格式与 C++ 版本一致）
        model_path = args.model_path
        print(f"正在加载 ONNX 模型: {model_path}")
        predictor = OnnxSpectrumPredictor(model_path)
        print("模型加载成功！")
        print()
        
        # 生成随机测试数据（与 C++ 版本一致，使用相同的随机数生成方式）
        # C++ 使用 rand()，Python 尝试使用 C 库的 rand() 函数（如果可用）
        try:
            import ctypes
            import ctypes.util
            libc = ctypes.CDLL(ctypes.util.find_library('c'))
            RAND_MAX = 2147483647
            
            class CRand:
                """使用 C 库的 rand() 函数（与 C++ 完全一致）"""
                def __init__(self, seed=None):
                    if seed is not None:
                        libc.srand(seed)
                    # 如果不设置种子，C 库会使用默认种子（与 C++ 一致）
                
                def random(self):
                    """返回 0.0 到 1.0 之间的随机浮点数（模拟 rand() / RAND_MAX）"""
                    return libc.rand() / float(RAND_MAX)
            
            c_rand = CRand(args.seed)
        except:
            # 如果无法使用 C 库，使用 Python 的 random（行为可能略有不同）
            import random
            if args.seed is not None:
                random.seed(args.seed)
            
            class CRand:
                """使用 Python random 模块（备用方案）"""
                def random(self):
                    return random.random()
            
            c_rand = CRand()
        
        # 单样本预测（格式与 C++ 版本一致）
        if not args.single_only:
            print("执行单样本预测...")
            # 创建测试数据（核心算法改动：使用动态检测的输入大小）
            test_spectrum = np.array([
                c_rand.random() * 10000.0 for _ in range(predictor.input_size)
            ], dtype=np.float32)
            prediction = predictor.predict(test_spectrum)
            # 格式化为与 C++ 一致的输出（不显示过多小数位）
            print(f"预测值: {prediction:.1f}")
            print()
        
        # 批量预测（格式与 C++ 版本一致）
        batch_size = args.batch_size if args.batch_size is not None else 3
        print("执行批量预测...")
        batch_spectra = []
        for i in range(batch_size):
            batch_spectra.append(np.array([
                c_rand.random() * 10000.0 for _ in range(predictor.input_size)
            ], dtype=np.float32))
        
        batch_predictions = predictor.predict_batch(batch_spectra)
        print("批量预测结果:")
        for i in range(len(batch_predictions)):
            # 格式化为与 C++ 一致的输出（不显示过多小数位）
            print(f"  样本 {i}: {batch_predictions[i]:.1f}")
        
    except FileNotFoundError as e:
        print(f"错误: 文件未找到 - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

