#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光谱数据预测程序
基于1024个光谱数据作为输入，预测一个输出值
包含训练和预测功能，数据集自动生成
"""

import numpy as np
import pickle
import os
import sys
import argparse
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional

# ONNX 相关导入
try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import FloatTensorType
    import onnx
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("警告: skl2onnx 或 onnx 未安装，ONNX 导出功能不可用")


class SpectrumPredictor:
    """光谱数据预测器"""
    
    def __init__(self, model_type='random_forest'):
        """
        初始化预测器
        
        Args:
            model_type: 模型类型，可选 'random_forest', 'linear', 'svm'
        """
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def generate_dataset(self, n_samples: int = 10000, noise_level: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        自动生成训练数据集
        
        Args:
            n_samples: 样本数量
            noise_level: 噪声水平
            
        Returns:
            X: 输入数据 (n_samples, 1024) - 1024个光谱数据点
            y: 输出数据 (n_samples,) - 预测目标值
        """
        print(f"正在生成 {n_samples} 个样本的数据集...")
        
        # 生成模拟光谱数据（1024个数据点）
        # 使用多个高斯峰模拟真实光谱特征
        X = np.zeros((n_samples, 1024))
        y = np.zeros(n_samples)
        
        for i in range(n_samples):
            # 生成基础光谱曲线（多个高斯峰的组合）
            x_axis = np.linspace(0, 1023, 1024)
            
            # 随机生成3-5个高斯峰
            n_peaks = np.random.randint(3, 6)
            spectrum = np.zeros(1024)
            
            for _ in range(n_peaks):
                # 随机峰位置
                peak_pos = np.random.uniform(100, 900)
                # 随机峰高度
                peak_height = np.random.uniform(1000, 10000)
                # 随机峰宽度
                peak_width = np.random.uniform(20, 100)
                
                # 高斯峰
                gaussian = peak_height * np.exp(-0.5 * ((x_axis - peak_pos) / peak_width) ** 2)
                spectrum += gaussian
            
            # 添加基线
            baseline = np.random.uniform(100, 500)
            spectrum += baseline
            
            # 添加噪声
            noise = np.random.normal(0, noise_level * np.max(spectrum), 1024)
            spectrum += noise
            
            # 确保非负
            spectrum = np.maximum(spectrum, 0)
            
            X[i] = spectrum
            
            # 生成目标值：基于光谱特征的组合
            # 例如：峰值总和、平均强度、峰值位置等
            peak_sum = np.sum(spectrum)
            peak_mean = np.mean(spectrum)
            peak_max = np.max(spectrum)
            peak_std = np.std(spectrum)
            
            # 目标值可以是这些特征的线性或非线性组合
            # 这里使用非线性组合模拟真实场景
            y[i] = (peak_sum * 0.0001 + 
                   peak_mean * 0.5 + 
                   peak_max * 0.3 + 
                   peak_std * 2.0 +
                   np.random.normal(0, 10))  # 添加一些随机性
        
        print(f"数据集生成完成: X形状={X.shape}, y形状={y.shape}")
        return X, y
    
    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.2, 
              random_state: int = 42, **kwargs):
        """
        训练模型
        
        Args:
            X: 输入数据 (n_samples, 1024)
            y: 输出数据 (n_samples,)
            test_size: 测试集比例
            random_state: 随机种子
            **kwargs: 模型参数
        """
        print("\n开始训练模型...")
        
        # 数据标准化
        X_scaled = self.scaler.fit_transform(X)
        
        # 划分训练集和测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_size, random_state=random_state
        )
        
        print(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
        
        # 创建并训练模型
        if self.model_type == 'random_forest':
            n_estimators = kwargs.get('n_estimators', 100)
            max_depth = kwargs.get('max_depth', None)
            self.model = RandomForestRegressor(
                n_estimators=n_estimators,
                max_depth=max_depth,
                random_state=random_state,
                n_jobs=-1
            )
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
        
        print("正在训练模型...")
        self.model.fit(X_train, y_train)
        self.is_trained = True
        
        # 评估模型
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        train_mae = mean_absolute_error(y_train, y_train_pred)
        test_mae = mean_absolute_error(y_test, y_test_pred)
        
        print("\n训练结果:")
        print(f"训练集 MSE: {train_mse:.4f}, R²: {train_r2:.4f}, MAE: {train_mae:.4f}")
        print(f"测试集 MSE: {test_mse:.4f}, R²: {test_r2:.4f}, MAE: {test_mae:.4f}")
        
        return {
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'train_mae': train_mae,
            'test_mae': test_mae
        }
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Args:
            X: 输入数据 (n_samples, 1024) 或单个样本 (1024,)
            
        Returns:
            预测结果
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练，请先调用 train() 方法")
        
        # 确保是2D数组
        X = np.array(X)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        
        # 标准化
        X_scaled = self.scaler.transform(X)
        
        # 预测
        predictions = self.model.predict(X_scaled)
        
        return predictions
    
    def save_model(self, filepath: str):
        """
        保存模型
        
        Args:
            filepath: 保存路径
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练，无法保存")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'is_trained': self.is_trained
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"模型已保存到: {filepath}")
    
    def load_model(self, filepath: str):
        """
        加载模型
        
        Args:
            filepath: 模型文件路径
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"模型文件不存在: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.is_trained = model_data['is_trained']
        
        print(f"模型已从 {filepath} 加载")
    
    def save_onnx_model(self, filepath: str, include_scaler: bool = True):
        """
        保存模型为 ONNX 格式（供 C++ 使用）
        
        Args:
            filepath: 保存路径（.onnx 文件）
            include_scaler: 是否包含标准化器（StandardScaler）
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练，无法保存")
        
        if not ONNX_AVAILABLE:
            raise ImportError("skl2onnx 或 onnx 未安装，无法导出 ONNX 格式。请运行: pip install skl2onnx onnx")
        
        try:
            from sklearn.pipeline import Pipeline
            
            # 定义输入类型：1024个浮点数
            initial_type = [('float_input', FloatTensorType([None, 1024]))]
            
            if include_scaler:
                # 创建包含标准化和模型的管道
                pipeline = Pipeline([
                    ('scaler', self.scaler),
                    ('model', self.model)
                ])
                onnx_model = convert_sklearn(pipeline, initial_types=initial_type)
            else:
                # 只转换模型（C++ 端需要手动进行标准化）
                onnx_model = convert_sklearn(self.model, initial_types=initial_type)
            
            # 保存 ONNX 模型
            with open(filepath, 'wb') as f:
                f.write(onnx_model.SerializeToString())
            
            # 验证模型
            onnx.checker.check_model(onnx_model)
            
            print(f"ONNX 模型已保存到: {filepath}")
            print(f"输入形状: [batch_size, 1024]")
            print(f"输出形状: [batch_size, 1]")
            if include_scaler:
                print("注意: 模型已包含标准化步骤，C++ 端无需手动标准化")
            else:
                print("警告: 模型不包含标准化步骤，C++ 端需要手动进行标准化")
            
            return onnx_model
            
        except Exception as e:
            raise RuntimeError(f"导出 ONNX 模型失败: {e}")


def plot_prediction_results(y_true: np.ndarray, y_pred: np.ndarray, 
                           title: str = "预测结果对比"):
    """
    绘制预测结果对比图
    
    Args:
        y_true: 真实值
        y_pred: 预测值
        title: 图表标题
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 
             'r--', lw=2, label='完美预测线')
    plt.xlabel('真实值')
    plt.ylabel('预测值')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('prediction_results.png', dpi=150)
    print("预测结果图已保存到: prediction_results.png")
    plt.close()


def plot_spectrum_example(spectrum: np.ndarray, title: str = "光谱数据示例"):
    """
    绘制光谱数据示例
    
    Args:
        spectrum: 光谱数据 (1024,)
        title: 图表标题
    """
    plt.figure(figsize=(12, 6))
    plt.plot(spectrum)
    plt.xlabel('数据点索引')
    plt.ylabel('强度')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('spectrum_example.png', dpi=150)
    print("光谱示例图已保存到: spectrum_example.png")
    plt.close()


# ==================== 示例函数 ====================

def example_basic_usage():
    """基本使用示例"""
    print("=" * 60)
    print("示例1: 基本使用")
    print("=" * 60)
    
    # 创建预测器
    predictor = SpectrumPredictor(model_type='random_forest')
    
    # 生成小规模数据集（用于快速测试）
    print("\n生成数据集...")
    X, y = predictor.generate_dataset(n_samples=1000, noise_level=0.1)
    
    # 训练模型
    print("\n训练模型...")
    results = predictor.train(X, y, test_size=0.2, n_estimators=50, max_depth=10)
    
    # 预测单个样本
    print("\n预测单个样本...")
    test_spectrum = X[0]
    prediction = predictor.predict(test_spectrum)
    print(f"输入光谱数据: 形状={test_spectrum.shape}")
    print(f"预测值: {prediction[0]:.2f}")
    print(f"真实值: {y[0]:.2f}")
    print(f"误差: {abs(prediction[0] - y[0]):.2f}")
    
    # 批量预测
    print("\n批量预测...")
    batch_predictions = predictor.predict(X[:10])
    print(f"批量预测结果: {batch_predictions}")
    print(f"真实值: {y[:10]}")


def example_save_and_load():
    """保存和加载模型示例"""
    print("\n" + "=" * 60)
    print("示例2: 保存和加载模型")
    print("=" * 60)
    
    # 创建并训练模型
    predictor = SpectrumPredictor()
    X, y = predictor.generate_dataset(n_samples=500, noise_level=0.1)
    predictor.train(X, y, n_estimators=50, max_depth=10)
    
    # 保存模型
    model_path = 'example_model.pkl'
    predictor.save_model(model_path)
    
    # 加载模型
    print("\n加载模型...")
    new_predictor = SpectrumPredictor()
    new_predictor.load_model(model_path)
    
    # 使用加载的模型预测
    test_spectrum = X[0]
    prediction = new_predictor.predict(test_spectrum)
    print(f"使用加载的模型预测: {prediction[0]:.2f}")
    print(f"真实值: {y[0]:.2f}")


def example_custom_data():
    """使用自定义数据示例"""
    print("\n" + "=" * 60)
    print("示例3: 使用自定义数据")
    print("=" * 60)
    
    # 创建自定义光谱数据（模拟从C++程序接收的数据）
    custom_spectrum = np.random.rand(1024) * 10000  # 模拟光谱数据
    
    # 如果有多个样本，可以这样组织
    custom_X = np.array([
        np.random.rand(1024) * 10000,
        np.random.rand(1024) * 10000,
        np.random.rand(1024) * 10000,
    ])
    
    # 对应的目标值（你需要根据实际情况提供）
    custom_y = np.array([100.5, 200.3, 150.7])
    
    # 训练模型
    predictor = SpectrumPredictor()
    predictor.train(custom_X, custom_y, n_estimators=50, max_depth=10)
    
    # 预测新数据
    new_spectrum = np.random.rand(1024) * 10000
    prediction = predictor.predict(new_spectrum)
    print(f"新光谱数据预测值: {prediction[0]:.2f}")


def example_integration_with_cpp():
    """与C++程序集成的示例说明"""
    print("\n" + "=" * 60)
    print("示例4: 与C++程序集成")
    print("=" * 60)
    
    print("""
    如果你需要从C++程序（如calc_app）中调用Python预测程序，可以：
    
    1. 在C++中使用QProcess调用Python脚本：
       ```cpp
       QProcess process;
       QStringList arguments;
       arguments << "spectrum_predictor.py" << "--predict" << dataFile;
       process.start("python3", arguments);
       ```
    
    2. 或者使用Python C API嵌入Python解释器
    
    3. 或者通过文件/网络接口传递数据：
       - C++程序将光谱数据保存为CSV/JSON文件
       - Python程序读取文件并进行预测
       - Python程序将结果写回文件
       - C++程序读取预测结果
    
    4. 或者使用PyQt/PySide在Python中直接调用C++Qt对象
    
    5. 推荐方式：导出ONNX模型，在C++中使用ONNX Runtime
    """)


def run_examples():
    """运行所有示例"""
    try:
        example_basic_usage()
        example_save_and_load()
        example_custom_data()
        example_integration_with_cpp()
        
        print("\n" + "=" * 60)
        print("所有示例执行完成！")
        print("=" * 60)
        
    except ImportError as e:
        print(f"\n错误: 缺少依赖库 - {e}")
        print("请运行: pip install -r requirements.txt")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


def export_onnx_quick(n_samples=5000, onnx_path='spectrum_model.onnx'):
    """快速导出 ONNX 模型"""
    print("=" * 60)
    print("ONNX 模型导出工具")
    print("=" * 60)
    
    # 创建预测器
    predictor = SpectrumPredictor(model_type='random_forest')
    
    # 生成数据集（使用较小的数据集以加快速度）
    print("\n生成训练数据集...")
    X, y = predictor.generate_dataset(n_samples=n_samples, noise_level=0.1)
    
    # 训练模型
    print("\n训练模型...")
    predictor.train(X, y, test_size=0.2, n_estimators=100, max_depth=20)
    
    # 导出 ONNX 模型
    print(f"\n导出 ONNX 模型到: {onnx_path}")
    
    try:
        predictor.save_onnx_model(onnx_path, include_scaler=True)
        print("\n✓ 导出成功！")
        print(f"\n模型文件: {onnx_path}")
        print("输入: [batch_size, 1024] 浮点数组")
        print("输出: [batch_size, 1] 浮点数组（预测值）")
        print("\n现在可以在 C++ 程序中使用此模型了！")
        print("参考 README_ONNX.md 了解如何在 C++ 中使用。")
        
        # 验证导出
        print("\n验证导出模型...")
        test_sample = X[0:1]
        
        # Python 预测
        python_pred = predictor.predict(test_sample)[0]
        
        # 尝试使用 ONNX Runtime 验证（如果可用）
        try:
            import onnxruntime as ort
            session = ort.InferenceSession(onnx_path)
            input_name = session.get_inputs()[0].name
            # 确保数据类型为 float32（ONNX 模型要求）
            test_sample_float32 = test_sample.astype(np.float32)
            onnx_output = session.run(None, {input_name: test_sample_float32})[0]
            # 确保 onnx_pred 是标量值
            onnx_pred = float(onnx_output.flatten()[0]) if isinstance(onnx_output, np.ndarray) else float(onnx_output[0])
            
            print(f"Python 预测: {python_pred:.4f}")
            print(f"ONNX 预测:  {onnx_pred:.4f}")
            print(f"差异:       {abs(python_pred - onnx_pred):.6f}")
            
            if abs(python_pred - onnx_pred) < 0.01:
                print("✓ 验证通过：ONNX 模型预测结果与 Python 模型一致")
            else:
                print("⚠ 警告：预测结果存在差异，可能是正常的浮点误差")
        except ImportError:
            print("(跳过 ONNX Runtime 验证，需要安装: pip install onnxruntime)")
        except Exception as e:
            print(f"(ONNX Runtime 验证失败: {e})")
        
    except Exception as e:
        print(f"\n✗ 导出失败: {e}")
        print("\n请确保已安装必要的依赖:")
        print("  pip install skl2onnx onnx")
        sys.exit(1)


def main_full():
    """完整训练和预测流程"""
    print("=" * 60)
    print("光谱数据预测程序 - 完整流程")
    print("=" * 60)
    
    # 创建预测器
    predictor = SpectrumPredictor(model_type='random_forest')
    
    # 生成数据集
    X, y = predictor.generate_dataset(n_samples=10000, noise_level=0.1)
    
    # 显示一个光谱数据示例
    print("\n显示第一个光谱数据示例:")
    print(f"数据点数量: {len(X[0])}")
    print(f"最小值: {X[0].min():.2f}, 最大值: {X[0].max():.2f}, 平均值: {X[0].mean():.2f}")
    print(f"对应的目标值: {y[0]:.2f}")
    
    # 绘制光谱示例
    plot_spectrum_example(X[0], "生成的光谱数据示例")
    
    # 训练模型
    results = predictor.train(X, y, test_size=0.2, n_estimators=100, max_depth=20)
    
    # 绘制预测结果
    X_test_scaled = predictor.scaler.transform(X[len(X)//5:])  # 使用部分数据作为测试
    y_test = y[len(X)//5:]
    y_pred = predictor.predict(X_test_scaled)
    plot_prediction_results(y_test, y_pred, "模型预测结果对比")
    
    # 保存模型（pickle 格式，用于 Python）
    model_path = 'spectrum_model.pkl'
    predictor.save_model(model_path)
    
    # 保存 ONNX 模型（供 C++ 使用）
    print("\n导出 ONNX 模型...")
    try:
        onnx_path = 'spectrum_model.onnx'
        predictor.save_onnx_model(onnx_path, include_scaler=True)
        print(f"✓ ONNX 模型已导出: {onnx_path}")
        print("  可以在 C++ 程序中使用 ONNX Runtime 加载此模型")
    except Exception as e:
        print(f"✗ ONNX 导出失败: {e}")
        print("  请安装依赖: pip install skl2onnx onnx")
    
    # 测试加载模型
    print("\n测试模型加载...")
    new_predictor = SpectrumPredictor()
    new_predictor.load_model(model_path)
    
    # 使用加载的模型进行预测
    test_sample = X[0:1]  # 取第一个样本
    prediction = new_predictor.predict(test_sample)
    print(f"\n使用加载的模型预测第一个样本:")
    print(f"输入光谱数据: 形状={test_sample.shape}")
    print(f"预测值: {prediction[0]:.2f}")
    print(f"真实值: {y[0]:.2f}")
    print(f"误差: {abs(prediction[0] - y[0]):.2f}")
    
    print("\n" + "=" * 60)
    print("程序执行完成！")
    print("=" * 60)


def main():
    """主函数 - 支持命令行参数"""
    parser = argparse.ArgumentParser(
        description='光谱数据预测程序 - 基于1024个光谱数据点预测输出值',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 导出 ONNX 模型（默认）
  python3 spectrum_predictor.py
  
  # 自定义 ONNX 导出参数
  python3 spectrum_predictor.py --samples 10000 --output model.onnx
  
  # 完整流程（训练+预测+可视化）
  python3 spectrum_predictor.py --mode full
  
  # 运行示例代码
  python3 spectrum_predictor.py --mode examples
        """
    )
    
    parser.add_argument(
        '--mode',
        choices=['full', 'export-onnx', 'examples'],
        default='export-onnx',
        help='运行模式: full=完整流程, export-onnx=导出ONNX模型(默认), examples=运行示例'
    )
    
    parser.add_argument(
        '--export-onnx',
        action='store_true',
        help='快速导出 ONNX 模型（等同于 --mode export-onnx）'
    )
    
    parser.add_argument(
        '--examples',
        action='store_true',
        help='运行示例代码（等同于 --mode examples）'
    )
    
    parser.add_argument(
        '--samples',
        type=int,
        default=5000,
        help='生成数据集样本数量（用于 ONNX 导出，默认: 5000）'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='spectrum_model.onnx',
        help='ONNX 模型输出路径（默认: spectrum_model.onnx）'
    )
    
    args = parser.parse_args()
    
    # 处理简化的命令行参数
    if args.export_onnx:
        args.mode = 'export-onnx'
    elif args.examples:
        args.mode = 'examples'
    
    # 根据模式执行相应功能
    if args.mode == 'export-onnx':
        export_onnx_quick(n_samples=args.samples, onnx_path=args.output)
    elif args.mode == 'examples':
        run_examples()
    else:  # full
        main_full()


if __name__ == '__main__':
    main()

