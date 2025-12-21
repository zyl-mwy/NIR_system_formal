#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
光谱数据预测程序 - PyTorch 版本
基于1024个光谱数据作为输入，预测一个输出值
使用 PyTorch 训练神经网络模型，导出为 .jit 格式
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import os
import sys
import argparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from typing import Tuple, List, Optional


class SpectrumDataset(Dataset):
    """光谱数据集"""
    
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


class SpectrumNet(nn.Module):
    """光谱预测神经网络"""
    
    def __init__(self, input_size=1024, hidden_sizes=[512, 256, 128], dropout=0.2):
        super(SpectrumNet, self).__init__()
        
        layers = []
        prev_size = input_size
        
        for hidden_size in hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            prev_size = hidden_size
        
        # 输出层
        layers.append(nn.Linear(prev_size, 1))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x).squeeze()


class SpectrumPredictor:
    """光谱数据预测器 - PyTorch 版本"""
    
    def __init__(self, input_size=1024):
        self.input_size = input_size
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"使用设备: {self.device}")
        
    def generate_dataset(self, n_samples: int = 10000, noise_level: float = 0.1) -> Tuple[np.ndarray, np.ndarray]:
        """
        自动生成训练数据集
        
        Args:
            n_samples: 样本数量
            noise_level: 噪声水平
            
        Returns:
            X: 光谱数据 (n_samples, 1024)
            y: 目标值 (n_samples,)
        """
        np.random.seed(42)
        
        # 生成模拟光谱数据
        X = np.random.randn(n_samples, self.input_size)
        
        # 添加一些特征：模拟真实光谱的特征
        # 1. 添加基线漂移
        baseline = np.linspace(0, 0.5, self.input_size)
        X = X + baseline[np.newaxis, :]
        
        # 2. 添加峰值特征
        peak_positions = np.random.randint(0, self.input_size, size=(n_samples, 5))
        for i in range(n_samples):
            for pos in peak_positions[i]:
                X[i, pos] += np.random.randn() * 2
        
        # 3. 归一化
        X = (X - X.min(axis=1, keepdims=True)) / (X.max(axis=1, keepdims=True) - X.min(axis=1, keepdims=True) + 1e-8)
        
        # 生成目标值：基于光谱数据的加权和
        weights = np.random.randn(self.input_size)
        y = np.dot(X, weights) + np.random.randn(n_samples) * noise_level
        
        # 归一化目标值到合理范围
        y = (y - y.mean()) / y.std() * 10 + 50  # 均值50，标准差10
        
        return X, y
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray, 
              epochs: int = 100, batch_size: int = 32, lr: float = 0.001,
              hidden_sizes: List[int] = [512, 256, 128], dropout: float = 0.2):
        """
        训练模型
        
        Args:
            X_train: 训练数据
            y_train: 训练标签
            epochs: 训练轮数
            batch_size: 批次大小
            lr: 学习率
            hidden_sizes: 隐藏层大小列表
            dropout: Dropout 比率
        """
        print(f"开始训练 PyTorch 模型...")
        print(f"训练数据形状: {X_train.shape}, 标签形状: {y_train.shape}")
        
        # 数据标准化
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # 创建数据集和数据加载器
        train_dataset = SpectrumDataset(X_train_scaled, y_train)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # 创建模型
        self.model = SpectrumNet(input_size=self.input_size, 
                                 hidden_sizes=hidden_sizes, 
                                 dropout=dropout).to(self.device)
        
        # 损失函数和优化器
        criterion = nn.MSELoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=10)
        
        # 训练循环
        self.model.train()
        train_losses = []
        
        for epoch in range(epochs):
            epoch_loss = 0.0
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                # 前向传播
                optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = criterion(outputs, batch_y)
                
                # 反向传播
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(train_loader)
            train_losses.append(avg_loss)
            scheduler.step(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.6f}")
        
        self.is_trained = True
        print("训练完成！")
        
        return train_losses
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict:
        """
        评估模型
        
        Args:
            X_test: 测试数据
            y_test: 测试标签
            
        Returns:
            评估指标字典
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        self.model.eval()
        X_test_scaled = self.scaler.transform(X_test)
        X_test_tensor = torch.FloatTensor(X_test_scaled).to(self.device)
        
        with torch.no_grad():
            y_pred_tensor = self.model(X_test_tensor)
            y_pred = y_pred_tensor.cpu().numpy()
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        metrics = {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        print("\n评估结果:")
        for key, value in metrics.items():
            print(f"{key}: {value:.6f}")
        
        return metrics
    
    def save_jit_model(self, filepath: str):
        """
        保存为 JIT 格式模型
        
        Args:
            filepath: 保存路径
        
        注意：
            - 无论训练时使用的是 GPU 还是 CPU，导出时都会将模型移到 CPU
            - 这样可以确保导出的 JIT 模型可以在任何设备上加载使用（包括 C++ 接口）
            - 如果训练时使用 GPU，导出后模型会自动移回 GPU，不影响后续训练或推理
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        self.model.eval()
        
        # 保存当前设备，以便导出后恢复
        original_device = next(self.model.parameters()).device
        
        # 【重要】将模型临时移到 CPU 进行导出
        # 原因：如果使用 GPU 训练，torch.jit.trace 会记录设备信息
        #       导出的 JIT 模型会包含 GPU 设备信息，导致在 CPU 上加载失败
        #       或者在 C++ 接口中无法正常使用
        # 解决方案：导出前将模型移到 CPU，确保导出的模型是 CPU 兼容的
        self.model = self.model.cpu()
        
        # 创建示例输入（标准化后的），确保在 CPU 上
        # 注意：示例输入也必须在 CPU 上，与模型设备保持一致
        example_input = torch.FloatTensor(self.scaler.transform(np.zeros((1, self.input_size))))
        # 明确指定在 CPU 上（虽然默认就是 CPU，但为了代码清晰性）
        example_input = example_input.to('cpu')
        
        # 导出为 TorchScript（此时模型和输入都在 CPU 上）
        traced_model = torch.jit.trace(self.model, example_input)
        traced_model.save(filepath)
        
        # 【可选】如果原来在 GPU 上训练，将模型移回 GPU
        # 这样如果后续还需要继续使用这个模型进行训练或推理，可以继续使用 GPU
        # 注意：如果后续不再使用 GPU，可以注释掉这行以节省显存
        if original_device.type == 'cuda':
            self.model = self.model.to(original_device)
            print(f"模型已移回原设备: {original_device}")
        
        print(f"模型已保存为 JIT 格式: {filepath}")
        print(f"注意：导出的 JIT 模型是 CPU 兼容的，可以在任何设备上加载使用")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Args:
            X: 输入数据
            
        Returns:
            预测结果
        """
        if not self.is_trained:
            raise ValueError("模型尚未训练")
        
        self.model.eval()
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled).to(self.device)
        
        with torch.no_grad():
            y_pred_tensor = self.model(X_tensor)
            y_pred = y_pred_tensor.cpu().numpy()
        
        return y_pred


def main():
    parser = argparse.ArgumentParser(description='PyTorch 光谱数据预测器训练')
    parser.add_argument('--input-size', type=int, default=1024, help='输入维度')
    parser.add_argument('--epochs', type=int, default=100, help='训练轮数')
    parser.add_argument('--batch-size', type=int, default=32, help='批次大小')
    parser.add_argument('--lr', type=float, default=0.001, help='学习率')
    parser.add_argument('--n-samples', type=int, default=10000, help='训练样本数')
    parser.add_argument('--output', type=str, default='spectrum_model.jit', help='输出模型文件名')
    
    args = parser.parse_args()
    
    # 创建预测器
    predictor = SpectrumPredictor(input_size=args.input_size)
    
    # 生成数据集
    print("生成数据集...")
    X, y = predictor.generate_dataset(n_samples=args.n_samples)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"训练集大小: {X_train.shape[0]}, 测试集大小: {X_test.shape[0]}")
    
    # 训练模型
    predictor.train(X_train, y_train, 
                   epochs=args.epochs, 
                   batch_size=args.batch_size, 
                   lr=args.lr)
    
    # 评估模型
    metrics = predictor.evaluate(X_test, y_test)
    
    # 保存模型
    output_path = os.path.join(os.path.dirname(__file__), args.output)
    predictor.save_jit_model(output_path)
    
    print(f"\n训练完成！模型已保存到: {output_path}")
    print(f"模型评估指标: R2={metrics['R2']:.4f}, RMSE={metrics['RMSE']:.4f}")


if __name__ == '__main__':
    main()

