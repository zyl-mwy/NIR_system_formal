import QtQuick 6.5
import QtQuick.Controls 6.5

Window {
    id: root
    width: 800
    height: 600
    visible: true
    title: "简易插件计算器 (Qt6 + QML)"

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

    Column {
        spacing: 12
        anchors.fill: parent
        anchors.margins: 16

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
            width: parent.width
            height: 1
            color: "#cccccc"
        }

        Row {
            spacing: 8
            Label { 
                text: "串口:" 
                anchors.verticalCenter: parent.verticalCenter
            }
            TextField {
                id: serialPortInput
                text: "/dev/ttyUSB0"
                width: 200
                placeholderText: "例如: /dev/ttyUSB0"
            }
            Button {
                text: serialComm.isStarted ? "发送停止命令" : "发送启动命令"
                onClicked: {
                    const port = serialPortInput.text.trim()
                    if (port.length === 0) {
                        serialStatusLabel.text = "✗ 请输入串口名称"
                        return
                    }
                    serialComm.toggleCommand(port)
                }
            }
        }

        Label {
            id: serialStatusLabel
            text: "串口状态将在这里显示"
            wrapMode: Label.Wrap
            color: "#666666"
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#cccccc"
        }

        Row {
            spacing: 8
            Label { 
                text: "UDP端口:" 
                anchors.verticalCenter: parent.verticalCenter
            }
            TextField {
                id: udpPortInput
                text: "1234"
                width: 100
                inputMethodHints: Qt.ImhDigitsOnly
                placeholderText: "端口号"
            }
            Label { 
                text: "绑定地址:" 
                anchors.verticalCenter: parent.verticalCenter
            }
            TextField {
                id: udpBindAddressInput
                text: "192.168.1.102"
                width: 150
                placeholderText: "留空为任意地址"
            }
            Button {
                text: udpComm.receiving ? "停止UDP接收" : "启动UDP接收"
                onClicked: {
                    if (udpComm.receiving) {
                        udpComm.stopReceiving()
                    } else {
                        const port = parseInt(udpPortInput.text)
                        if (isNaN(port) || port < 1 || port > 65535) {
                            udpStatusLabel.text = "✗ 请输入有效的端口号(1-65535)"
                            return
                        }
                        const bindAddr = udpBindAddressInput.text.trim()
                        udpComm.startReceiving(port, bindAddr)
                    }
                }
            }
        }

        Label {
            id: udpStatusLabel
            text: "UDP状态将在这里显示"
            wrapMode: Label.Wrap
            color: "#666666"
        }

        Row {
            spacing: 8
            Label {
                text: "已接收光谱数据:"
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
        }

        Label {
            id: udpPacketInfoLabel
            text: "最新数据包信息将在这里显示"
            wrapMode: Label.Wrap
            color: "#333333"
            font.pixelSize: 11
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#cccccc"
        }

        Row {
            spacing: 8
            Label {
                text: "黑参考:"
                color: "#333333"
                font.bold: true
            }
            Button {
                text: udpComm.blackReferenceAccumulating ? "停止黑参考" : "开始黑参考"
                enabled: udpComm.receiving && !udpComm.blackReferenceAccumulating || udpComm.blackReferenceAccumulating
                onClicked: {
                    if (udpComm.blackReferenceAccumulating) {
                        udpComm.stopBlackReference()
                    } else {
                        udpComm.startBlackReference()
                    }
                }
            }
            Label {
                text: "进度:"
                color: "#333333"
            }
            Label {
                id: blackReferenceProgressLabel
                text: udpComm.blackReferenceProgress.toString() + " / 39500"
                color: udpComm.blackReferenceAccumulating ? "#0066cc" : "#666666"
                font.bold: udpComm.blackReferenceAccumulating
                font.pixelSize: 14
            }
        }

        Row {
            spacing: 8
            Label {
                text: "白参考:"
                color: "#333333"
                font.bold: true
            }
            Button {
                text: udpComm.whiteReferenceAccumulating ? "停止白参考" : "开始白参考"
                enabled: udpComm.receiving && !udpComm.whiteReferenceAccumulating || udpComm.whiteReferenceAccumulating
                onClicked: {
                    if (udpComm.whiteReferenceAccumulating) {
                        udpComm.stopWhiteReference()
                    } else {
                        udpComm.startWhiteReference()
                    }
                }
            }
            Label {
                text: "进度:"
                color: "#333333"
            }
            Label {
                id: whiteReferenceProgressLabel
                text: udpComm.whiteReferenceProgress.toString() + " / 39500"
                color: udpComm.whiteReferenceAccumulating ? "#0066cc" : "#666666"
                font.bold: udpComm.whiteReferenceAccumulating
                font.pixelSize: 14
            }
        }

        Rectangle {
            width: parent.width
            height: 1
            color: "#cccccc"
        }

        Label {
            text: "光谱曲线 (每3950条数据更新一次，后台线程处理)"
            font.bold: true
            color: "#333333"
        }

        Rectangle {
            id: spectrumChartContainer
            width: parent.width
            height: 200
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
            // 更新黑参考进度显示
            blackReferenceProgressLabel.text = progress.toString() + " / 39500"
        }

        function onBlackReferenceReady(averagedSpectrum, minVal, maxVal) {
            // 黑参考数据处理完成，可以在这里保存或使用黑参考数据
            blackReferenceData = averagedSpectrum
            blackReferenceMinVal = minVal
            blackReferenceMaxVal = maxVal
            console.log("黑参考数据处理完成，平均值范围:", minVal, "~", maxVal)
        }

        function onWhiteReferenceProgressChanged(progress) {
            // 更新白参考进度显示
            whiteReferenceProgressLabel.text = progress.toString() + " / 39500"
        }

        function onWhiteReferenceReady(averagedSpectrum, minVal, maxVal) {
            // 白参考数据处理完成，可以在这里保存或使用白参考数据
            whiteReferenceData = averagedSpectrum
            whiteReferenceMinVal = minVal
            whiteReferenceMaxVal = maxVal
            console.log("白参考数据处理完成，平均值范围:", minVal, "~", maxVal)
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
}


