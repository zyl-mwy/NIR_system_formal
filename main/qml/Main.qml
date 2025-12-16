import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

Window {
    id: root
    width: 1000
    height: 700
    minimumWidth: 800
    minimumHeight: 600
    visible: true
    title: "近红外水分检测系统"

    onClosing: function(close) {
        // 关闭界面时，如果串口还在运行状态，自动发送停止命令
        if (serialComm.isStarted) {
            const port = serialPortInput.text.trim()
            if (port.length > 0) {
                serialComm.sendStopCommand(port)
            } else {
                // 如果输入框为空，使用默认值
                serialComm.sendStopCommand("/dev/ttyUSB0")
            }
        }
        // 允许窗口关闭
        close.accepted = true
    }

    ScrollView {
        id: scrollView
        anchors.fill: parent
        clip: true
        
        Item {
            width: scrollView.availableWidth
            implicitHeight: contentColumn.implicitHeight + 32
            
            ColumnLayout {
                id: contentColumn
                width: parent.width
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.right: parent.right
                anchors.margins: 16
                spacing: 16
            
            RowLayout {
                spacing: 16
                Layout.fillWidth: true

            // 左侧：串口和UDP设置
            ColumnLayout {
                spacing: 12
                Layout.preferredWidth: 350
                Layout.minimumWidth: 300
                Layout.maximumWidth: 400

                Label {
                    text: "通信设置"
                    font.bold: true
                    color: "#333333"
                    font.pixelSize: 16
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }

                // 串口设置
                Label {
                    text: "串口配置"
                    font.bold: true
                    color: "#333333"
                    font.pixelSize: 14
                }

                RowLayout {
                    spacing: 8
                    Label { 
                        text: "串口:" 
                        Layout.preferredWidth: 60
                    }
                    TextField {
                        id: serialPortInput
                        text: "/dev/ttyUSB0"
                        Layout.fillWidth: true
                        placeholderText: "例如: /dev/ttyUSB0"
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }

                // UDP设置
                Label {
                    text: "UDP配置"
                    font.bold: true
                    color: "#333333"
                    font.pixelSize: 14
                }

                RowLayout {
                    spacing: 8
                    Label { 
                        text: "地址:" 
                        Layout.preferredWidth: 50
                    }
                    TextField {
                        id: udpBindAddressInput
                        text: "192.168.1.102"
                        Layout.fillWidth: true
                        placeholderText: "留空为任意地址"
                    }
                    Label { 
                        text: "端口:" 
                        Layout.preferredWidth: 50
                    }
                    TextField {
                        id: udpPortInput
                        text: "1234"
                        Layout.preferredWidth: 80
                        inputMethodHints: Qt.ImhDigitsOnly
                        placeholderText: "端口号"
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }

                // 共用启动按钮和通信修正按钮
                RowLayout {
                    spacing: 8
                    Layout.fillWidth: true
                    
                    Button {
                        Layout.fillWidth: true
                        text: (serialComm.isStarted || udpComm.receiving) ? "停止获取光谱" : "开始获取光谱"
                        onClicked: {
                            if (serialComm.isStarted || udpComm.receiving) {
                                // 停止所有通信
                                if (serialComm.isStarted) {
                                    const port = serialPortInput.text.trim()
                                    if (port.length > 0) {
                                        serialComm.toggleCommand(port)
                                    }
                                }
                                if (udpComm.receiving) {
                                    udpComm.stopReceiving()
                                }
                            } else {
                                // 启动所有通信
                                // 启动串口
                                const port = serialPortInput.text.trim()
                                if (port.length > 0) {
                                    serialComm.toggleCommand(port)
                                } else {
                                    serialStatusLabel.text = "✗ 请输入串口名称"
                                }
                                
                                // 启动UDP
                                const udpPort = parseInt(udpPortInput.text)
                                if (isNaN(udpPort) || udpPort < 1 || udpPort > 65535) {
                                    udpStatusLabel.text = "✗ 请输入有效的端口号(1-65535)"
                                } else {
                                    const bindAddr = udpBindAddressInput.text.trim()
                                    udpComm.startReceiving(udpPort, bindAddr)
                                }
                            }
                        }
                    }
                    
                    Button {
                        Layout.preferredWidth: 100
                        text: "通信修正"
                        onClicked: {
                            // 只发送开始检测的命令，不做其他操作
                            const port = serialPortInput.text.trim()
                            if (port.length > 0) {
                                serialComm.sendStartCommand(port)
                            } else {
                                serialStatusLabel.text = "✗ 请输入串口名称"
                            }
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }

                // 参考数据处理
                Label {
                    text: "参考数据处理"
                    font.bold: true
                    color: "#333333"
                    font.pixelSize: 14
                }

                RowLayout {
                    spacing: 8
                    Label {
                        text: "黑参考:"
                        color: "#333333"
                        font.bold: true
                        Layout.preferredWidth: 60
                    }
                    Button {
                        text: udpComm.blackReferenceAccumulating ? "停止黑参考" : "开始黑参考"
                        enabled: udpComm.receiving && !udpComm.blackReferenceAccumulating || udpComm.blackReferenceAccumulating
                        Layout.fillWidth: true
                        onClicked: {
                            if (udpComm.blackReferenceAccumulating) {
                                udpComm.stopBlackReference()
                            } else {
                                // 清除之前的成功标记，以便重新显示进度
                                blackReferenceData = null
                                udpComm.startBlackReference()
                            }
                        }
                    }
                }

                RowLayout {
                    spacing: 8
                    Label {
                        text: "进度:"
                        color: "#333333"
                        Layout.preferredWidth: 60
                    }
                    Label {
                        id: blackReferenceProgressLabel
                        text: blackReferenceData !== null ? "已经成功获取" : (udpComm.blackReferenceProgress.toString() + " / 39500")
                        color: blackReferenceData !== null ? "#006600" : (udpComm.blackReferenceAccumulating ? "#0066cc" : "#666666")
                        font.bold: blackReferenceData !== null || udpComm.blackReferenceAccumulating
                        font.pixelSize: 14
                        Layout.fillWidth: true
                    }
                }

                RowLayout {
                    spacing: 8
                    Label {
                        text: "白参考:"
                        color: "#333333"
                        font.bold: true
                        Layout.preferredWidth: 60
                    }
                    Button {
                        text: udpComm.whiteReferenceAccumulating ? "停止白参考" : "开始白参考"
                        enabled: udpComm.receiving && !udpComm.whiteReferenceAccumulating || udpComm.whiteReferenceAccumulating
                        Layout.fillWidth: true
                        onClicked: {
                            if (udpComm.whiteReferenceAccumulating) {
                                udpComm.stopWhiteReference()
                            } else {
                                // 清除之前的成功标记，以便重新显示进度
                                whiteReferenceData = null
                                udpComm.startWhiteReference()
                            }
                        }
                    }
                }

                RowLayout {
                    spacing: 8
                    Label {
                        text: "进度:"
                        color: "#333333"
                        Layout.preferredWidth: 60
                    }
                    Label {
                        id: whiteReferenceProgressLabel
                        text: whiteReferenceData !== null ? "已经成功获取" : (udpComm.whiteReferenceProgress.toString() + " / 39500")
                        color: whiteReferenceData !== null ? "#006600" : (udpComm.whiteReferenceAccumulating ? "#0066cc" : "#666666")
                        font.bold: whiteReferenceData !== null || udpComm.whiteReferenceAccumulating
                        font.pixelSize: 14
                        Layout.fillWidth: true
                    }
                }
            }

            // 右侧：其他内容
            ColumnLayout {
                spacing: 12
                Layout.fillWidth: true

                // 数字计算器功能已暂时屏蔽
                /*
                Row {
                    spacing: 8
                    Label { text: "数字 A:" }
                    TextField {
                        id: inputA
                        text: "1"
                        width: 140
                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                    }

                    Label { text: "数字 B:" }
                    TextField {
                        id: inputB
                        text: "2"
                        width: 140
                        inputMethodHints: Qt.ImhFormattedNumbersOnly
                    }
                }

                Row {
                    spacing: 8
                    Label { text: "选择算法插件:" }
                    ComboBox {
                        id: pluginBox
                        model: pluginManager.pluginNames
                        enabled: pluginManager.hasPlugins()
                        width: 240
                    }
                }

                Row {
                    spacing: 12
                    Button {
                        text: "计算"
                        enabled: pluginManager.hasPlugins()
                        onClicked: {
                            const a = Number(inputA.text)
                            const b = Number(inputB.text)

                            if (Number.isNaN(a) || Number.isNaN(b)) {
                                resultLabel.text = "请输入有效数字"
                                return
                            }

                            const res = pluginManager.compute(pluginBox.currentIndex, a, b)
                            if (res === undefined || res === null) {
                                resultLabel.text = "计算失败，可能未找到插件"
                                return
                            }

                            resultLabel.text = "结果: " + res
                        }
                    }

                    Label {
                        id: resultLabel
                        text: pluginManager.hasPlugins() ? "结果将在这里显示" : "未找到可用插件"
                        wrapMode: Label.Wrap
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }
                */

                // 预测器配置区域
                Label {
                    text: "预测算法配置"
                    font.bold: true
                    color: "#333333"
                    font.pixelSize: 14
                    Layout.fillWidth: true
                }

                ColumnLayout {
                    spacing: 8
                    Layout.fillWidth: true

                    RowLayout {
                        spacing: 8
                        Label {
                            text: "选择预测算法:"
                            color: "#333333"
                            Layout.preferredWidth: 120
                        }
                        ComboBox {
                            id: predictorComboBox
                            model: predictorManager.predictorNames
                            enabled: predictorManager.hasPredictors
                            Layout.preferredWidth: 280
                            Layout.fillWidth: true
                    onCurrentIndexChanged: {
                        if (currentIndex >= 0) {
                            const algorithm = predictorManager.getAlgorithm(currentIndex)
                            predictorStatusLabel.text = "已选择: " + currentText + " (算法: " + algorithm + ")"
                            predictorStatusLabel.color = "#666666"
                            
                            // 更新当前模型加载状态
                            currentModelLoaded = predictorManager.isModelLoaded(currentIndex)
                            
                            // 记住切换前的预测状态（是否已启用预测）
                            const wasPredicting = currentPredictorIndex >= 0
                            
                            // 如果已经有预测器在运行，且切换到了不同的预测器，先禁用旧的
                            if (wasPredicting && currentPredictorIndex !== currentIndex) {
                                udpComm.setPredictorIndex(-1)
                                currentPredictorIndex = -1
                                predictionResultLabel.text = "正在切换预测器..."
                                predictionResultLabel.color = "#0066cc"
                            }
                            
                            // 自动加载对应文件夹的模型
                            const modelPath = predictorManager.getDefaultModelPath(currentIndex)
                            if (modelPath.length > 0) {
                                predictorStatusLabel.text = "正在加载模型: " + modelPath
                                predictorStatusLabel.color = "#0066cc"
                                
                                // 延迟加载，确保界面更新
                                Qt.callLater(function() {
                                    const success = predictorManager.loadModelAuto(currentIndex)
                                    if (success) {
                                        predictorStatusLabel.text = "✓ 模型自动加载成功"
                                        predictorStatusLabel.color = "#006600"
                                        
                                        // 如果之前有预测器在运行，自动启用新的预测器
                                        if (wasPredicting && success) {
                                            udpComm.setPredictorIndex(currentIndex)
                                            currentPredictorIndex = currentIndex
                                            predictionResultLabel.text = "预测已切换到新算法，等待数据..."
                                            predictionResultLabel.color = "#0066cc"
                                        }
                                    } else {
                                        predictorStatusLabel.text = "✗ 模型自动加载失败: " + modelPath
                                        predictorStatusLabel.color = "#cc0000"
                                    }
                                })
                            } else {
                                predictorStatusLabel.text = "✗ 无法找到默认模型路径"
                                predictorStatusLabel.color = "#cc0000"
                            }
                        } else {
                            currentModelLoaded = false
                            // 如果选择了无效项，禁用预测
                            if (currentPredictorIndex >= 0) {
                                udpComm.setPredictorIndex(-1)
                                currentPredictorIndex = -1
                                predictionResultLabel.text = "预测已禁用"
                                predictionResultLabel.color = "#666666"
                            }
                        }
                            }
                        }
                    }

                    RowLayout {
                        spacing: 8
                        Label {
                            text: "预测状态:"
                            color: "#333333"
                            Layout.preferredWidth: 120
                        }
                        Label {
                            id: modelLoadedLabel
                            text: predictorComboBox.currentIndex >= 0 && currentModelLoaded ? "模型已加载" : "模型未加载"
                            color: predictorComboBox.currentIndex >= 0 && currentModelLoaded ? "#006600" : "#cc0000"
                            font.bold: true
                        }
                        Label {
                            text: "|"
                            color: "#cccccc"
                        }
                        Button {
                            text: currentPredictorIndex >= 0 ? "禁用预测" : "启用预测"
                            enabled: predictorComboBox.currentIndex >= 0 && currentModelLoaded && (udpComm.receiving || serialComm.isStarted)
                            Layout.preferredWidth: 150
                            Layout.fillWidth: true
                            onClicked: {
                                if (currentPredictorIndex >= 0) {
                                    udpComm.setPredictorIndex(-1)
                                    currentPredictorIndex = -1
                                    predictionResultLabel.text = "预测已禁用"
                                    predictionResultLabel.color = "#666666"
                                } else {
                                    const index = predictorComboBox.currentIndex
                                    udpComm.setPredictorIndex(index)
                                    currentPredictorIndex = index
                                    predictionResultLabel.text = "预测已启用，等待数据..."
                                    predictionResultLabel.color = "#0066cc"
                                }
                            }
                        }
                    }

                    Label {
                        id: predictorStatusLabel
                        text: "请选择预测算法并加载模型"
                        wrapMode: Label.Wrap
                        color: "#666666"
                        font.pixelSize: 11
                        Layout.fillWidth: true
                    }

                    RowLayout {
                        spacing: 8
                        Label {
                            text: "预测结果:"
                            color: "#333333"
                            font.bold: true
                        }
                        Label {
                            id: predictionResultLabel
                            text: "未启用预测"
                            color: "#666666"
                            font.bold: true
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                    }
                }

                Rectangle {
                    Layout.fillWidth: true
                    height: 1
                    color: "#cccccc"
                }

                Label {
                    text: "光谱曲线 (每3950条数据更新一次，后台线程处理)"
                    font.bold: true
                    color: "#333333"
                    Layout.fillWidth: true
                }

                Rectangle {
                    id: spectrumChartContainer
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    Layout.fillHeight: true
            color: "#f5f5f5"
            border.color: "#cccccc"
            border.width: 1

            Canvas {
                id: spectrumCanvas
                anchors.fill: parent
                anchors.margins: 10

                onPaint: {
                    var ctx = getContext("2d")
                    ctx.clearRect(0, 0, width, height)
                    
                    if (!spectrumData || spectrumData.length === 0) {
                        ctx.fillStyle = "#999999"
                        ctx.font = "14px sans-serif"
                        ctx.fillText("等待数据...", width / 2 - 50, height / 2)
                        return
                    }

                    var dataPoints = spectrumData.length
                    if (dataPoints === 0) return

                    // 使用后台线程处理好的数据
                    var minVal = spectrumMinVal
                    var maxVal = spectrumMaxVal
                    var range = maxVal - minVal
                    if (range === 0) range = 1  // 避免除零

                    // 绘制坐标轴
                    ctx.strokeStyle = "#cccccc"
                    ctx.lineWidth = 1
                    ctx.beginPath()
                    ctx.moveTo(0, height - 1)
                    ctx.lineTo(width, height - 1)
                    ctx.moveTo(0, height - 1)
                    ctx.lineTo(0, 0)
                    ctx.stroke()

                    // 绘制曲线
                    ctx.strokeStyle = "#0066cc"
                    ctx.lineWidth = 2
                    ctx.beginPath()
                    
                    var stepX = width / (dataPoints - 1)
                    for (var i = 0; i < dataPoints; i++) {
                        var x = i * stepX
                        var value = spectrumData[i]
                        // 归一化到0-height范围，并翻转Y轴（因为Canvas的Y轴向下）
                        var normalized = (value - minVal) / range
                        var y = height - 1 - normalized * (height - 2)
                        
                        if (i === 0) {
                            ctx.moveTo(x, y)
                        } else {
                            ctx.lineTo(x, y)
                        }
                    }
                    ctx.stroke()

                    // 绘制信息文本
                    ctx.fillStyle = "#333333"
                    ctx.font = "12px sans-serif"
                    ctx.fillText("最小值: " + minVal.toFixed(0), 10, 20)
                    ctx.fillText("最大值: " + maxVal.toFixed(0), 10, 35)
                    ctx.fillText("数据包数: " + spectrumPacketCount, 10, 50)
                }
            }
        }
            }
            }
            
            // 状态信息区域（界面下方，左右分栏）
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 120
                spacing: 16
                
                // 左下角：通信状态信息
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#f5f5f5"
                    border.color: "#cccccc"
                    border.width: 1
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        
                        Label {
                            text: "通信状态信息"
                            font.bold: true
                            color: "#333333"
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#cccccc"
                        }
                        
                        // 串口通信状态
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "串口状态:"
                                color: "#333333"
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: serialStatusLabel
                                text: "串口状态将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#666666"
                                Layout.fillWidth: true
                            }
                        }
                        
                        // UDP通信状态
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "UDP状态:"
                                color: "#333333"
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: udpStatusLabel
                                text: "UDP状态将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#666666"
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
                
                // 右下角：其他信息
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#f5f5f5"
                    border.color: "#cccccc"
                    border.width: 1
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 12
                        spacing: 8
                        
                        Label {
                            text: "UDP信息统计"
                            font.bold: true
                            color: "#333333"
                            font.pixelSize: 14
                            Layout.fillWidth: true
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: "#cccccc"
                        }
                        
                        // UDP信息统计
                        RowLayout {
                            spacing: 12
                            Label {
                                text: "已接收:"
                                color: "#333333"
                            }
                            Label {
                                id: packetCountLabel
                                text: udpComm.packetCount.toString()
                                color: "#006600"
                                font.bold: true
                                font.pixelSize: 14
                            }
                            Label {
                                text: "条"
                                color: "#333333"
                            }
                            Label {
                                text: "|"
                                color: "#cccccc"
                            }
                            Label {
                                text: "接收速率:"
                                color: "#333333"
                            }
                            Label {
                                id: rateLabel
                                text: udpComm.packetsPerSecond.toString()
                                color: "#0066cc"
                                font.bold: true
                                font.pixelSize: 14
                            }
                            Label {
                                text: "条/秒"
                                color: "#333333"
                            }
                            Button {
                                text: "重置计数"
                                onClicked: udpComm.resetPacketCount()
                            }
                            Item { Layout.fillWidth: true }
                        }
                        
                        // UDP数据包信息
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "数据包信息:"
                                color: "#333333"
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: udpPacketInfoLabel
                                text: "最新数据包信息将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#333333"
                                font.pixelSize: 11
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
            }
            }
        }
    }

    Connections {
        target: udpComm
        function onStatusChanged(message) {
            udpStatusLabel.text = message
            if (message.startsWith("✓")) {
                udpStatusLabel.color = "#006600"
            } else if (message.startsWith("✗")) {
                udpStatusLabel.color = "#cc0000"
            } else {
                udpStatusLabel.color = "#666666"
            }
        }

        function onPacketReceived(data) {
            // 使用Timer延迟更新，避免高频更新导致界面卡顿
            if (!updateTimer.running) {
                updateTimer.start()
            }
            // 保存最新的数据包信息
            lastPacketInfo = {
                dataLength: data.length
            }
        }

        function onSpectrumReady(averagedSpectrum, minVal, maxVal, packetCount) {
            // 接收到后台线程处理好的光谱数据，更新显示（在主线程中执行，不阻塞）
            spectrumData = averagedSpectrum
            spectrumMinVal = minVal
            spectrumMaxVal = maxVal
            spectrumPacketCount = packetCount
            spectrumCanvas.requestPaint()
        }

        function onBlackReferenceProgressChanged(progress) {
            // 进度更新会自动通过绑定更新显示
            // 如果已成功获取，标签会显示"已经成功获取"
        }

        function onBlackReferenceReady(averagedSpectrum, minVal, maxVal) {
            // 黑参考数据处理完成，可以在这里保存或使用黑参考数据
            blackReferenceData = averagedSpectrum
            blackReferenceMinVal = minVal
            blackReferenceMaxVal = maxVal
            console.log("黑参考数据处理完成，平均值范围:", minVal, "~", maxVal)
        }

        function onWhiteReferenceProgressChanged(progress) {
            // 进度更新会自动通过绑定更新显示
            // 如果已成功获取，标签会显示"已经成功获取"
        }

        function onWhiteReferenceReady(averagedSpectrum, minVal, maxVal) {
            // 白参考数据处理完成，可以在这里保存或使用白参考数据
            whiteReferenceData = averagedSpectrum
            whiteReferenceMinVal = minVal
            whiteReferenceMaxVal = maxVal
            console.log("白参考数据处理完成，平均值范围:", minVal, "~", maxVal)
        }

        function onPredictionReady(predictorIndex, predictionValue) {
            // 接收到预测结果
            if (currentPredictorIndex === predictorIndex) {
                predictionResultLabel.text = "预测值: " + predictionValue.toFixed(4)
                predictionResultLabel.color = "#006600"
                console.log("预测结果 [预测器", predictorIndex, "]:", predictionValue)
            }
        }
    }

    Connections {
        target: predictorManager
        function onModelLoaded(index, success) {
            // 如果加载的是当前选中的预测器，更新界面状态
            if (index === predictorComboBox.currentIndex) {
                currentModelLoaded = success
                if (success) {
                    modelLoadedLabel.text = "模型已加载"
                    modelLoadedLabel.color = "#006600"
                } else {
                    modelLoadedLabel.text = "模型未加载"
                    modelLoadedLabel.color = "#cc0000"
                }
            }
        }
    }

    Timer {
        id: updateTimer
        interval: 50  // 50ms更新一次，平衡响应速度和性能
        onTriggered: {
            if (lastPacketInfo) {
                udpPacketInfoLabel.text = "数据点数: " + lastPacketInfo.dataLength
            }
        }
    }

    property var lastPacketInfo: null
    property var spectrumData: null  // 存储处理好的光谱数据
    property double spectrumMinVal: 0
    property double spectrumMaxVal: 0
    property int spectrumPacketCount: 0
    property var blackReferenceData: null  // 存储黑参考数据
    property double blackReferenceMinVal: 0
    property double blackReferenceMaxVal: 0
    property var whiteReferenceData: null  // 存储白参考数据
    property double whiteReferenceMinVal: 0
    property double whiteReferenceMaxVal: 0
    property int currentPredictorIndex: -1  // 当前使用的预测器索引（-1表示未启用）
    property bool currentModelLoaded: false  // 当前选中预测器的模型加载状态

    Connections {
        target: serialComm
        function onStatusChanged(message) {
            serialStatusLabel.text = message
            if (message.startsWith("✓")) {
                serialStatusLabel.color = "#006600"
            } else if (message.startsWith("✗")) {
                serialStatusLabel.color = "#cc0000"
            } else {
                serialStatusLabel.color = "#666666"
            }
        }
    }

    // 监听预测器管理器的模型加载信号，更新界面状态
    Connections {
        target: predictorManager
        function onModelLoaded(index, success) {
            // 如果加载的是当前选中的预测器，更新界面
            if (index === predictorComboBox.currentIndex) {
                // 强制更新按钮的 enabled 状态
                // 通过触发一个属性变化来强制 QML 重新评估绑定
                if (success) {
                    modelLoadedLabel.text = "模型已加载"
                    modelLoadedLabel.color = "#006600"
                } else {
                    modelLoadedLabel.text = "模型未加载"
                    modelLoadedLabel.color = "#cc0000"
                }
            }
        }
    }
}


