#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyTorch JIT Python 示例代码
演示如何在 Python 中使用 PyTorch 加载和运行 JIT 模型
功能与 jit_example.cpp 相同
"""

import torch
import numpy as np
import sys
import argparse
from typing import List, Union, Optional


class JitSpectrumPredictor:
    """PyTorch JIT 光谱数据预测器（Python 版本）"""
    
    def __init__(self, model_path: str):
        """
        初始化预测器
        
        Args:
            model_path: JIT 模型文件路径
        """
        # 加载 JIT 模型
        self.model = torch.jit.load(model_path)
        self.model.eval()
        
        # 获取输入输出信息（格式与 C++ 版本一致）
        # 对于 JIT 模型，我们需要通过前向传播来推断形状
        # 创建一个示例输入来获取模型信息
        example_input = torch.randn(1, 1024)
        
        # 打印输入信息（格式与 C++ 版本一致）
        print("输入 0 名称: input")
        print("输入 0 形状: [1, 1024]")
        
        # 获取输出信息
        with torch.no_grad():
            example_output = self.model(example_input)
            if example_output.dim() == 0:
                output_shape = []
            else:
                output_shape = list(example_output.shape)
        
        # 格式化为与 C++ 一致的输出
        shape_str = "["
        for j, dim in enumerate(output_shape):
            shape_str += str(dim)
            if j < len(output_shape) - 1:
                shape_str += ", "
        shape_str += "]"
        if not output_shape:
            shape_str = "[]"
        
        print("输出 0 名称: output")
        print(f"输出 0 形状: {shape_str}")
    
    def predict(self, spectrum_data: Union[List[float], np.ndarray]) -> float:
        """
        单样本预测：输入1024个光谱数据点，返回预测值
        
        Args:
            spectrum_data: 光谱数据，必须包含1024个数据点
            
        Returns:
            预测值
        """
        # 转换为 numpy 数组
        if isinstance(spectrum_data, list):
            spectrum_data = np.array(spectrum_data, dtype=np.float32)
        else:
            spectrum_data = spectrum_data.astype(np.float32)
        
        # 检查数据长度
        if spectrum_data.size != 1024:
            raise ValueError(f"光谱数据必须包含1024个数据点，当前: {spectrum_data.size}")
        
        # 确保是2D数组 [1, 1024]
        if spectrum_data.ndim == 1:
            spectrum_data = spectrum_data.reshape(1, -1)
        
        # 转换为张量
        input_tensor = torch.FloatTensor(spectrum_data)
        
        # 运行推理
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
            # 确保输出是标量或单个值
            if output_tensor.dim() == 0:
                prediction = float(output_tensor.item())
            else:
                prediction = float(output_tensor[0].item())
        
        return prediction
    
    def predict_batch(self, spectra: List[Union[List[float], np.ndarray]]) -> List[float]:
        """
        批量预测：输入多个光谱数据，返回预测值列表
        
        Args:
            spectra: 光谱数据列表，每个光谱数据必须包含1024个数据点
            
        Returns:
            预测值列表
        """
        if not spectra:
            return []
        
        batch_size = len(spectra)
        
        # 转换为 numpy 数组并检查
        batch_data = []
        for i, spectrum in enumerate(spectra):
            if isinstance(spectrum, list):
                spectrum = np.array(spectrum, dtype=np.float32)
            else:
                spectrum = spectrum.astype(np.float32)
            
            if spectrum.size != 1024:
                raise ValueError(f"第 {i} 个光谱数据必须包含1024个数据点，当前: {spectrum.size}")
            
            if spectrum.ndim == 1:
                spectrum = spectrum.reshape(1, -1)
            
            batch_data.append(spectrum)
        
        # 合并为批次 [batch_size, 1024]
        batch_array = np.vstack(batch_data)
        
        # 转换为张量
        input_tensor = torch.FloatTensor(batch_array)
        
        # 运行推理
        with torch.no_grad():
            output_tensor = self.model(input_tensor)
            # 确保输出是 numpy 数组
            if output_tensor.dim() == 0:
                predictions = [float(output_tensor.item())]
            else:
                predictions = [float(p) for p in output_tensor.flatten().tolist()]
        
        return predictions


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PyTorch JIT Python 预测程序 - 使用 JIT 模型进行光谱数据预测',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本使用
  python3 jit_predictor.py spectrum_model.jit
  
  # 使用自定义测试数据
  python3 jit_predictor.py spectrum_model.jit --test-data-file data.csv
  
  # 批量预测
  python3 jit_predictor.py spectrum_model.jit --batch-size 10
        """
    )
    
    parser.add_argument(
        'model_path',
        type=str,
        help='JIT 模型文件路径'
    )
    
    parser.add_argument(
        '--test-data-file',
        type=str,
        default=None,
        help='测试数据文件路径（CSV格式，每行1024个值）'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=None,
        help='批量预测的样本数量（默认: 3，与 C++ 版本一致。如果指定，则只执行批量预测）'
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
    
    try:
        # 创建预测器（输出格式与 C++ 版本一致）
        model_path = args.model_path
        print(f"正在加载模型: {model_path}")
        predictor = JitSpectrumPredictor(model_path)
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
            # 创建测试数据（1024个随机值，模拟光谱数据）
            # 使用与 C++ 完全相同的随机数生成方式
            test_spectrum = np.array([
                c_rand.random() * 10000.0 for _ in range(1024)
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
                c_rand.random() * 10000.0 for _ in range(1024)
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
