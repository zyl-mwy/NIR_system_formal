import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5
import QtQuick.Dialogs 6.5

ApplicationWindow {
    id: root
    width: 1000
    height: 700
    minimumWidth: 800
    minimumHeight: 600
    visible: true
    title: "近红外水分检测系统"
    color: "#f5f6fa"

    // 顶部菜单栏：提供单次光谱采集入口
    menuBar: MenuBar {
        Menu {
            title: "采集"
            MenuItem {
                text: "单次光谱采集与记录"
                onTriggered: {
                    singleSpectrumWindow.visible = true
                    singleSpectrumWindow.raise()
                    singleSpectrumWindow.requestActivate()
                }
            }
        }
    }

    // 根据内容自动调整窗口大小
    function adjustWindowSize() {
        // 如果窗口是最大化状态，不自动调整大小
        if (root.visibility === Window.Maximized) {
            return
        }
        if (contentColumn.implicitHeight > 0) {
            var newHeight = contentColumn.implicitHeight + 32 + 40  // 内容高度 + 边距 + 标题栏
            var targetHeight = Math.max(minimumHeight, Math.min(newHeight, screen.desktopAvailableHeight * 0.95))
            if (Math.abs(root.height - targetHeight) > 10) {  // 增加阈值，避免频繁调整
                root.height = targetHeight
            }
        }
    }

    Timer {
        id: resizeTimer
        interval: 500
        running: root.visibility !== Window.Maximized
        repeat: true
        onTriggered: adjustWindowSize()
    }

    // 监听窗口状态变化
    onVisibilityChanged: {
        if (root.visibility === Window.Maximized) {
            resizeTimer.running = false
        } else {
            resizeTimer.running = true
        }
    }

    Component.onCompleted: {
        // 初始化时延迟调整窗口大小
        Qt.callLater(function() {
            if (root.visibility !== Window.Maximized) {
                adjustWindowSize()
            }
        })
    }

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
            Rectangle {
                Layout.preferredWidth: 260
                Layout.minimumWidth: 240
                Layout.maximumWidth: 300
                Layout.fillHeight: true
                color: "#ffffff"
                radius: 10
                border.color: "#e0e0e0"
                border.width: 1
                
                // 阴影效果
                Rectangle {
                    anchors.fill: parent
                    anchors.margins: -3
                    color: "transparent"
                    border.color: "#d0d0d0"
                    border.width: 1
                    radius: 13
                    z: -1
                    opacity: 0.2
                }
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.topMargin: 8
                    anchors.bottomMargin: 12
                    anchors.leftMargin: 12
                    anchors.rightMargin: 12
                    spacing: 8

                    // 串口设置
                    Label {
                        text: "串口配置"
                        font.bold: true
                        color: "#34495e"
                        font.pixelSize: 12
                        Layout.topMargin: 0
                    }

                    RowLayout {
                        spacing: 6
                        Label { 
                            text: "串口:" 
                            Layout.preferredWidth: 48
                            color: "#555555"
                            font.pixelSize: 12
                        }
                        TextField {
                            id: serialPortInput
                            text: "/dev/ttyUSB0"
                            Layout.fillWidth: true
                            placeholderText: "例如: /dev/ttyUSB0"
                            background: Rectangle {
                                color: "#f8f9fa"
                                border.color: serialPortInput.focus ? "#3498db" : "#dee2e6"
                                border.width: serialPortInput.focus ? 2 : 1
                                radius: 4
                            }
                            padding: 6
                            font.pixelSize: 12
                        }
                    }

                    // UDP设置
                    Label {
                        text: "UDP配置"
                        font.bold: true
                        color: "#34495e"
                        font.pixelSize: 12
                        Layout.topMargin: 0
                    }

                    RowLayout {
                        spacing: 6
                        Label { 
                            text: "地址:" 
                            Layout.preferredWidth: 48
                            color: "#555555"
                            font.pixelSize: 12
                        }
                        TextField {
                            id: udpBindAddressInput
                            text: "192.168.1.102"
                            Layout.fillWidth: true
                            placeholderText: "留空为任意地址"
                            background: Rectangle {
                                color: "#f8f9fa"
                                border.color: udpBindAddressInput.focus ? "#3498db" : "#dee2e6"
                                border.width: udpBindAddressInput.focus ? 2 : 1
                                radius: 4
                            }
                            padding: 6
                            font.pixelSize: 12
                        }
                        Label { 
                            text: "端口:" 
                            Layout.preferredWidth: 40
                            color: "#555555"
                            font.pixelSize: 12
                        }
                        TextField {
                            id: udpPortInput
                            text: "1234"
                            Layout.preferredWidth: 65
                            inputMethodHints: Qt.ImhDigitsOnly
                            placeholderText: "端口号"
                            background: Rectangle {
                                color: "#f8f9fa"
                                border.color: udpPortInput.focus ? "#3498db" : "#dee2e6"
                                border.width: udpPortInput.focus ? 2 : 1
                                radius: 4
                            }
                            padding: 6
                            font.pixelSize: 12
                        }
                    }

                    // 共用启动按钮和通信修正按钮
                    RowLayout {
                        spacing: 6
                        Layout.fillWidth: true
                        Layout.topMargin: 0
                        
                        Button {
                            Layout.fillWidth: true
                            text: (serialComm.isStarted || udpComm.receiving) ? "停止获取光谱" : "开始获取光谱"
                            background: Rectangle {
                                color: parent.pressed ? "#2980b9" : (parent.hovered ? "#3498db" : "#3498db")
                                radius: 6
                                border.color: "#2980b9"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 13
                                font.bold: true
                            }
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
                            Layout.preferredWidth: 85
                            text: "通信修正"
                            enabled: serialComm.isStarted || udpComm.receiving
                            background: Rectangle {
                                color: parent.pressed ? "#95a5a6" : (parent.hovered ? "#bdc3c7" : (parent.enabled ? "#ecf0f1" : "#e9ecef"))
                                radius: 6
                                border.color: parent.enabled ? "#bdc3c7" : "#d5d8dc"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: parent.enabled ? "#2c3e50" : "#95a5a6"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
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

                    // 参考数据处理
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.topMargin: 4
                        height: 1
                        color: "#e8e8e8"
                    }
                    
                    Label {
                        text: "参考数据处理"
                        font.bold: true
                        color: "#34495e"
                        font.pixelSize: 12
                        Layout.topMargin: 0
                    }

                    RowLayout {
                        spacing: 6
                        Label {
                            text: "黑参考:"
                            color: "#555555"
                            font.bold: true
                            Layout.preferredWidth: 52
                            font.pixelSize: 12
                        }
                        Button {
                            text: udpComm.blackReferenceAccumulating ? "停止黑参考" : "开始黑参考"
                            enabled: (udpComm.receiving && !udpComm.blackReferenceAccumulating && !udpComm.whiteReferenceAccumulating) || udpComm.blackReferenceAccumulating
                            Layout.fillWidth: true
                            background: Rectangle {
                                color: parent.pressed ? "#27ae60" : (parent.hovered ? "#2ecc71" : (parent.enabled ? "#27ae60" : "#bdc3c7"))
                                radius: 6
                                border.color: parent.enabled ? "#229954" : "#95a5a6"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: parent.enabled ? "#ffffff" : "#7f8c8d"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
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
                            color: "#555555"
                            Layout.preferredWidth: 52
                            font.pixelSize: 12
                        }
                        Label {
                            id: blackReferenceProgressLabel
                            text: blackReferenceData !== null ? "已经成功获取" : (udpComm.blackReferenceProgress.toString() + " / 39500")
                            color: blackReferenceData !== null ? "#27ae60" : (udpComm.blackReferenceAccumulating ? "#3498db" : "#7f8c8d")
                            font.bold: blackReferenceData !== null || udpComm.blackReferenceAccumulating
                            font.pixelSize: 12
                            Layout.fillWidth: true
                        }
                    }

                    RowLayout {
                        spacing: 8
                        Layout.topMargin: 4
                        Label {
                            text: "白参考:"
                            color: "#555555"
                            font.bold: true
                            Layout.preferredWidth: 52
                            font.pixelSize: 12
                        }
                        Button {
                            text: udpComm.whiteReferenceAccumulating ? "停止白参考" : "开始白参考"
                            enabled: (udpComm.receiving && !udpComm.whiteReferenceAccumulating && !udpComm.blackReferenceAccumulating) || udpComm.whiteReferenceAccumulating
                            Layout.fillWidth: true
                            background: Rectangle {
                                color: parent.pressed ? "#e67e22" : (parent.hovered ? "#f39c12" : (parent.enabled ? "#e67e22" : "#bdc3c7"))
                                radius: 6
                                border.color: parent.enabled ? "#d35400" : "#95a5a6"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: parent.enabled ? "#ffffff" : "#7f8c8d"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
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
                            color: "#555555"
                            Layout.preferredWidth: 52
                            font.pixelSize: 12
                        }
                        Label {
                            id: whiteReferenceProgressLabel
                            text: whiteReferenceData !== null ? "已经成功获取" : (udpComm.whiteReferenceProgress.toString() + " / 39500")
                            color: whiteReferenceData !== null ? "#27ae60" : (udpComm.whiteReferenceAccumulating ? "#3498db" : "#7f8c8d")
                            font.bold: whiteReferenceData !== null || udpComm.whiteReferenceAccumulating
                            font.pixelSize: 12
                            Layout.fillWidth: true
                        }
                    }
                }
            }

            // 右侧：其他内容
            ColumnLayout {
                spacing: 16
                Layout.fillWidth: true

                // 第一部分：预测算法配置
                Rectangle {
                    Layout.fillWidth: true
                    color: "#ffffff"
                    radius: 10
                    border.color: "#e0e0e0"
                    border.width: 1
                    implicitHeight: predictorConfigColumn.implicitHeight + 20
                    
                    // 阴影效果
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -3
                        color: "transparent"
                        border.color: "#d0d0d0"
                        border.width: 1
                        radius: 13
                        z: -1
                        opacity: 0.2
                    }
                    
                    ColumnLayout {
                        id: predictorConfigColumn
                        anchors.fill: parent
                        anchors.topMargin: 8
                        anchors.bottomMargin: 12
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 8

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
                    color: "#34495e"
                    font.pixelSize: 12
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
                            Layout.preferredHeight: 32
                            Layout.fillWidth: true
                            
                            background: Rectangle {
                                color: "#f8f9fa"
                                border.color: parent.focus ? "#3498db" : "#dee2e6"
                                border.width: parent.focus ? 2 : 1
                                radius: 4
                            }
                            contentItem: Text {
                                text: parent.displayText
                                color: parent.enabled ? "#2c3e50" : "#95a5a6"
                                font.pixelSize: 12
                                verticalAlignment: Text.AlignVCenter
                                leftPadding: 8
                                rightPadding: 8
                            }
                            popup.background: Rectangle {
                                color: "#ffffff"
                                border.color: "#dee2e6"
                                border.width: 1
                                radius: 4
                            }
                            
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
                                // 清空预测历史
                                predictionHistory = []
                                predictionCanvas.requestPaint()
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
                                // 清空预测历史
                                predictionHistory = []
                                predictionCanvas.requestPaint()
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
                            
                            background: Rectangle {
                                color: parent.pressed ? "#7d3c98" : (parent.hovered ? "#9b59b6" : (parent.enabled ? "#9b59b6" : "#bdc3c7"))
                                radius: 6
                                border.color: parent.enabled ? "#7d3c98" : "#95a5a6"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: parent.enabled ? "#ffffff" : "#7f8c8d"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 13
                                font.bold: true
                            }
                            
                            onClicked: {
                                if (currentPredictorIndex >= 0) {
                                    udpComm.setPredictorIndex(-1)
                                    currentPredictorIndex = -1
                                    predictionResultLabel.text = "预测已禁用"
                                    predictionResultLabel.color = "#666666"
                                    // 清空预测历史
                                    predictionHistory = []
                                    predictionCanvas.requestPaint()
                                } else {
                                    const index = predictorComboBox.currentIndex
                                    udpComm.setPredictorIndex(index)
                                    currentPredictorIndex = index
                                    predictionResultLabel.text = "预测已启用，等待数据..."
                                    predictionResultLabel.color = "#0066cc"
                                    // 清空预测历史，重新开始
                                    predictionHistory = []
                                    predictionCanvas.requestPaint()
                                }
                            }
                        }
                    }

                    Label {
                        id: predictorStatusLabel
                        text: "请选择预测算法并加载模型"
                        wrapMode: Label.Wrap
                        color: "#666666"
                        font.pixelSize: 12
                        Layout.fillWidth: true
                    }

                    RowLayout {
                        spacing: 8
                        Label {
                            text: "预测结果:"
                            color: "#555555"
                            font.bold: true
                            font.pixelSize: 12
                        }
                        Label {
                            id: predictionResultLabel
                            text: "未启用预测"
                            color: "#666666"
                            font.bold: true
                            font.pixelSize: 13
                            Layout.fillWidth: true
                        }
                    }
                        }
                    }
                }

                // 第二部分：图表区域
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 300
                    Layout.minimumHeight: 250
                    color: "#ffffff"
                    radius: 10
                    border.color: "#e0e0e0"
                    border.width: 1
                    
                    // 阴影效果
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -3
                        color: "transparent"
                        border.color: "#d0d0d0"
                        border.width: 1
                        radius: 13
                        z: -1
                        opacity: 0.2
                    }
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.topMargin: 8
                        anchors.bottomMargin: 12
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 12

                        Label {
                            text: "光谱曲线与预测结果曲线"
                            font.bold: true
                            color: "#34495e"
                            font.pixelSize: 12
                            Layout.fillWidth: true
                        }

                    RowLayout {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 200
                    spacing: 12

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 4

                        Label {
                            text: "光谱曲线 (每3950条数据更新一次)"
                            font.bold: true
                            color: "#34495e"
                            font.pixelSize: 12
                            Layout.fillWidth: true
                        }

                        Rectangle {
                            id: spectrumChartContainer
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#ffffff"
                            border.color: "#e0e0e0"
                            border.width: 1
                            radius: 6

                            Canvas {
                                id: spectrumCanvas
                                anchors.fill: parent

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)
                                    
                                    if (!spectrumData || spectrumData.length === 0) {
                                        ctx.fillStyle = "#95a5a6"
                                        ctx.font = "13px sans-serif"
                                        ctx.textAlign = "center"
                                        ctx.fillText("等待数据...", width / 2, height / 2)
                                        return
                                    }

                                    var dataPoints = spectrumData.length
                                    if (dataPoints === 0) return

                                    // 使用后台线程处理好的数据
                                    var minVal = spectrumMinVal
                                    var maxVal = spectrumMaxVal
                                    var range = maxVal - minVal
                                    if (range === 0) range = 1  // 避免除零

                                    // 计算绘图区域（排除边距，为坐标轴标签和刻度留出空间）
                                    var leftMargin = 75   // 左侧边距（Y 轴标签和刻度，增加空间避免遮挡）
                                    var rightMargin = 20  // 右侧边距
                                    var topMargin = 30    // 顶部边距
                                    var bottomMargin = 50 // 底部边距（X 轴标签和刻度）
                                    
                                    var plotLeft = leftMargin
                                    var plotRight = width - rightMargin
                                    var plotTop = topMargin
                                    var plotBottom = height - bottomMargin
                                    var plotWidth = plotRight - plotLeft
                                    var plotHeight = plotBottom - plotTop

                                    // 绘制网格线
                                    ctx.strokeStyle = "#f0f0f0"
                                    ctx.lineWidth = 1
                                    ctx.setLineDash([3, 3])
                                    
                                    // 垂直网格线（X 方向）
                                    var gridCountX = 5
                                    for (var gx = 0; gx <= gridCountX; gx++) {
                                        var gridX = plotLeft + (plotWidth * gx / gridCountX)
                                        ctx.beginPath()
                                        ctx.moveTo(gridX, plotTop)
                                        ctx.lineTo(gridX, plotBottom)
                                        ctx.stroke()
                                    }
                                    
                                    // 水平网格线（Y 方向）
                                    var gridCountY = 5
                                    for (var gy = 0; gy <= gridCountY; gy++) {
                                        var gridY = plotTop + (plotHeight * gy / gridCountY)
                                        ctx.beginPath()
                                        ctx.moveTo(plotLeft, gridY)
                                        ctx.lineTo(plotRight, gridY)
                                        ctx.stroke()
                                    }
                                    
                                    ctx.setLineDash([])  // 重置虚线

                                    // 绘制坐标轴
                                    ctx.strokeStyle = "#bdc3c7"
                                    ctx.lineWidth = 1.5
                                    ctx.beginPath()
                                    ctx.moveTo(plotLeft, plotBottom)
                                    ctx.lineTo(plotRight, plotBottom)  // X 轴
                                    ctx.moveTo(plotLeft, plotBottom)
                                    ctx.lineTo(plotLeft, plotTop)  // Y 轴
                                    ctx.stroke()

                                    // 绘制 X 轴刻度
                                    ctx.strokeStyle = "#95a5a6"
                                    ctx.lineWidth = 1
                                    ctx.fillStyle = "#7f8c8d"
                                    ctx.font = "10px sans-serif"
                                    ctx.textAlign = "center"
                                    ctx.textBaseline = "top"
                                    
                                    for (var tx = 0; tx <= gridCountX; tx++) {
                                        var tickX = plotLeft + (plotWidth * tx / gridCountX)
                                        var xValue = (dataPoints - 1) * tx / gridCountX
                                        
                                        // 绘制刻度线
                                        ctx.beginPath()
                                        ctx.moveTo(tickX, plotBottom)
                                        ctx.lineTo(tickX, plotBottom + 5)
                                        ctx.stroke()
                                        
                                        // 绘制刻度值（确保在 Canvas 范围内）
                                        if (tickX >= 0 && tickX <= width) {
                                            ctx.fillText(xValue.toFixed(0), tickX, plotBottom + 8)
                                        }
                                    }
                                    
                                    // 绘制 Y 轴刻度
                                    ctx.textAlign = "right"
                                    ctx.textBaseline = "middle"
                                    for (var ty = 0; ty <= gridCountY; ty++) {
                                        var tickY = plotTop + (plotHeight * ty / gridCountY)
                                        var yValue = maxVal - (range * ty / gridCountY)
                                        
                                        // 绘制刻度线
                                        ctx.beginPath()
                                        ctx.moveTo(plotLeft - 5, tickY)
                                        ctx.lineTo(plotLeft, tickY)
                                        ctx.stroke()
                                        
                                        // 绘制刻度值（确保在 Canvas 范围内，显示小数，位置在标签左侧）
                                        if (tickY >= 0 && tickY <= height) {
                                            // 根据数值大小决定小数位数
                                            var decimals = range > 1000 ? 0 : (range > 100 ? 1 : (range > 10 ? 2 : 3))
                                            ctx.fillText(yValue.toFixed(decimals), plotLeft - 12, tickY)
                                        }
                                    }

                                    // 绘制坐标轴标签
                                    ctx.fillStyle = "#34495e"
                                    ctx.font = "bold 12px sans-serif"
                                    ctx.textAlign = "center"
                                    ctx.textBaseline = "top"
                                    // X 轴标签
                                    ctx.fillText("数据点索引", plotLeft + plotWidth / 2, plotBottom + 25)
                                    
                                    // Y 轴标签（旋转90度，放在最左侧避免遮挡刻度）
                                    ctx.save()
                                    ctx.translate(5, plotTop + plotHeight / 2)
                                    ctx.rotate(-Math.PI / 2)
                                    ctx.fillText("强度值", 0, 0)
                                    ctx.restore()

                                    // 绘制曲线
                                    ctx.strokeStyle = "#0066cc"
                                    ctx.lineWidth = 2
                                    ctx.beginPath()
                                    
                                    var stepX = plotWidth / (dataPoints - 1)
                                    for (var i = 0; i < dataPoints; i++) {
                                        var x = plotLeft + i * stepX
                                        var value = spectrumData[i]
                                        // 归一化到0-plotHeight范围，并翻转Y轴（因为Canvas的Y轴向下）
                                        var normalized = (value - minVal) / range
                                        var y = plotBottom - normalized * plotHeight
                                        
                                        if (i === 0) {
                                            ctx.moveTo(x, y)
                                        } else {
                                            ctx.lineTo(x, y)
                                        }
                                    }
                                    ctx.stroke()

                                    // 绘制信息文本
                                    ctx.fillStyle = "#555555"
                                    ctx.font = "11px sans-serif"
                                    ctx.textAlign = "left"
                                    ctx.fillText("最小值: " + minVal.toFixed(0), plotLeft + 5, plotTop + 15)
                                    ctx.fillText("最大值: " + maxVal.toFixed(0), plotLeft + 5, plotTop + 30)
                                    ctx.fillText("数据包数: " + spectrumPacketCount, plotLeft + 5, plotTop + 45)
                                }
                            }
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        spacing: 4

                        Label {
                            text: "预测结果曲线 (最多10个数值)"
                            font.bold: true
                            color: "#34495e"
                            font.pixelSize: 12
                            Layout.fillWidth: true
                        }

                        Rectangle {
                            id: predictionChartContainer
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            color: "#ffffff"
                            border.color: "#e0e0e0"
                            border.width: 1
                            radius: 6

                            Canvas {
                                id: predictionCanvas
                                anchors.fill: parent

                                onPaint: {
                                    var ctx = getContext("2d")
                                    ctx.clearRect(0, 0, width, height)
                                    
                                    if (!predictionHistory || predictionHistory.length === 0) {
                                        ctx.fillStyle = "#95a5a6"
                                        ctx.font = "13px sans-serif"
                                        ctx.textAlign = "center"
                                        ctx.fillText("等待预测结果...", width / 2, height / 2)
                                        return
                                    }

                                    var dataPoints = predictionHistory.length
                                    if (dataPoints === 0) return

                                    // 计算最小值和最大值（添加一些边距）
                                    var minVal = predictionHistory[0]
                                    var maxVal = predictionHistory[0]
                                    for (var i = 1; i < dataPoints; i++) {
                                        if (predictionHistory[i] < minVal) minVal = predictionHistory[i]
                                        if (predictionHistory[i] > maxVal) maxVal = predictionHistory[i]
                                    }
                                    var range = maxVal - minVal
                                    if (range === 0) {
                                        range = 1
                                        minVal -= 0.5
                                        maxVal += 0.5
                                    } else {
                                        // 添加 10% 的边距
                                        var margin = range * 0.1
                                        minVal -= margin
                                        maxVal += margin
                                        range = maxVal - minVal
                                    }

                                    // 计算绘图区域（排除边距，为坐标轴标签和刻度留出空间）
                                    var leftMargin = 75   // 左侧边距（Y 轴标签和刻度，增加空间避免遮挡）
                                    var rightMargin = 20  // 右侧边距
                                    var topMargin = 30    // 顶部边距
                                    var bottomMargin = 50 // 底部边距（X 轴标签和刻度）
                                    
                                    var plotLeft = leftMargin
                                    var plotRight = width - rightMargin
                                    var plotTop = topMargin
                                    var plotBottom = height - bottomMargin
                                    var plotWidth = plotRight - plotLeft
                                    var plotHeight = plotBottom - plotTop

                                    // 绘制网格线
                                    ctx.strokeStyle = "#f0f0f0"
                                    ctx.lineWidth = 1
                                    ctx.setLineDash([3, 3])
                                    
                                    // 垂直网格线（X 方向）
                                    var gridCountX = 5
                                    for (var gx = 0; gx <= gridCountX; gx++) {
                                        var gridX = plotLeft + (plotWidth * gx / gridCountX)
                                        ctx.beginPath()
                                        ctx.moveTo(gridX, plotTop)
                                        ctx.lineTo(gridX, plotBottom)
                                        ctx.stroke()
                                    }
                                    
                                    // 水平网格线（Y 方向）
                                    var gridCountY = 5
                                    for (var gy = 0; gy <= gridCountY; gy++) {
                                        var gridY = plotTop + (plotHeight * gy / gridCountY)
                                        ctx.beginPath()
                                        ctx.moveTo(plotLeft, gridY)
                                        ctx.lineTo(plotRight, gridY)
                                        ctx.stroke()
                                    }
                                    
                                    ctx.setLineDash([])  // 重置虚线

                                    // 绘制坐标轴
                                    ctx.strokeStyle = "#bdc3c7"
                                    ctx.lineWidth = 1.5
                                    ctx.beginPath()
                                    ctx.moveTo(plotLeft, plotBottom)
                                    ctx.lineTo(plotRight, plotBottom)  // X 轴
                                    ctx.moveTo(plotLeft, plotBottom)
                                    ctx.lineTo(plotLeft, plotTop)  // Y 轴
                                    ctx.stroke()

                                    // 绘制 X 轴刻度
                                    ctx.strokeStyle = "#95a5a6"
                                    ctx.lineWidth = 1
                                    ctx.fillStyle = "#7f8c8d"
                                    ctx.font = "10px sans-serif"
                                    ctx.textAlign = "center"
                                    ctx.textBaseline = "top"
                                    
                                    for (var tx = 0; tx <= gridCountX; tx++) {
                                        var tickX = plotLeft + (plotWidth * tx / gridCountX)
                                        var xValue = (dataPoints - 1) * tx / gridCountX
                                        
                                        // 绘制刻度线
                                        ctx.beginPath()
                                        ctx.moveTo(tickX, plotBottom)
                                        ctx.lineTo(tickX, plotBottom + 5)
                                        ctx.stroke()
                                        
                                        // 绘制刻度值（确保在 Canvas 范围内）
                                        if (tickX >= 0 && tickX <= width) {
                                            ctx.fillText(xValue.toFixed(0), tickX, plotBottom + 8)
                                        }
                                    }
                                    
                                    // 绘制 Y 轴刻度
                                    ctx.textAlign = "right"
                                    ctx.textBaseline = "middle"
                                    for (var ty = 0; ty <= gridCountY; ty++) {
                                        var tickY = plotTop + (plotHeight * ty / gridCountY)
                                        var yValue = maxVal - (range * ty / gridCountY)
                                        
                                        // 绘制刻度线
                                        ctx.beginPath()
                                        ctx.moveTo(plotLeft - 5, tickY)
                                        ctx.lineTo(plotLeft, tickY)
                                        ctx.stroke()
                                        
                                        // 绘制刻度值（确保在 Canvas 范围内，位置在标签左侧）
                                        if (tickY >= 0 && tickY <= height) {
                                            ctx.fillText(yValue.toFixed(4), plotLeft - 12, tickY)
                                        }
                                    }

                                    // 绘制坐标轴标签
                                    ctx.fillStyle = "#34495e"
                                    ctx.font = "bold 12px sans-serif"
                                    ctx.textAlign = "center"
                                    ctx.textBaseline = "top"
                                    // X 轴标签
                                    ctx.fillText("预测序号", plotLeft + plotWidth / 2, plotBottom + 25)
                                    
                                    // Y 轴标签（旋转90度，放在最左侧避免遮挡刻度）
                                    ctx.save()
                                    ctx.translate(5, plotTop + plotHeight / 2)
                                    ctx.rotate(-Math.PI / 2)
                                    ctx.fillText("预测值", 0, 0)
                                    ctx.restore()

                                    // 绘制曲线
                                    ctx.strokeStyle = "#cc6600"
                                    ctx.lineWidth = 2
                                    ctx.beginPath()
                                    
                                    var stepX = plotWidth / (dataPoints - 1)
                                    for (var i = 0; i < dataPoints; i++) {
                                        var x = plotLeft + i * stepX
                                        var value = predictionHistory[i]
                                        // 归一化到0-plotHeight范围，并翻转Y轴（因为Canvas的Y轴向下）
                                        var normalized = (value - minVal) / range
                                        var y = plotBottom - normalized * plotHeight
                                        
                                        if (i === 0) {
                                            ctx.moveTo(x, y)
                                        } else {
                                            ctx.lineTo(x, y)
                                        }
                                    }
                                    ctx.stroke()

                                    // 绘制数据点
                                    ctx.fillStyle = "#cc6600"
                                    for (var i = 0; i < dataPoints; i++) {
                                        var x = plotLeft + i * stepX
                                        var value = predictionHistory[i]
                                        var normalized = (value - minVal) / range
                                        var y = plotBottom - normalized * plotHeight
                                        ctx.beginPath()
                                        ctx.arc(x, y, 3, 0, 2 * Math.PI)
                                        ctx.fill()
                                    }

                                    // 绘制信息文本
                                    ctx.fillStyle = "#555555"
                                    ctx.font = "11px sans-serif"
                                    ctx.textAlign = "left"
                                    var actualMin = Math.min.apply(null, predictionHistory)
                                    var actualMax = Math.max.apply(null, predictionHistory)
                                    var currentValue = predictionHistory[predictionHistory.length - 1]
                                    ctx.fillText("最小值: " + actualMin.toFixed(4), plotLeft + 5, plotTop + 15)
                                    ctx.fillText("最大值: " + actualMax.toFixed(4), plotLeft + 5, plotTop + 30)
                                    ctx.fillText("当前值: " + currentValue.toFixed(4), plotLeft + 5, plotTop + 45)
                                    ctx.fillText("数据点数: " + dataPoints + " / 10", plotLeft + 5, plotTop + 60)
                                }
                            }
                        }
                    }
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
                    color: "#ffffff"
                    radius: 10
                    border.color: "#e0e0e0"
                    border.width: 1
                    
                    // 阴影效果
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -3
                        color: "transparent"
                        border.color: "#d0d0d0"
                        border.width: 1
                        radius: 13
                        z: -1
                        opacity: 0.2
                    }
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.topMargin: 8
                        anchors.bottomMargin: 12
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 8
                        
                        // 标题区域
                        Rectangle {
                            Layout.fillWidth: true
                            height: 30
                            color: "#f8f9fa"
                            radius: 6
                            
                            Label {
                                anchors.left: parent.left
                                anchors.leftMargin: 10
                                anchors.verticalCenter: parent.verticalCenter
                                text: "通信状态信息"
                                font.bold: true
                                color: "#2c3e50"
                                font.pixelSize: 13
                            }
                        }
                        
                        // 串口通信状态
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "串口状态:"
                                color: "#555555"
                                font.pixelSize: 12
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: serialStatusLabel
                                text: "串口状态将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#666666"
                                font.pixelSize: 12
                                Layout.fillWidth: true
                            }
                        }
                        
                        // UDP通信状态
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "UDP状态:"
                                color: "#555555"
                                font.pixelSize: 12
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: udpStatusLabel
                                text: "UDP状态将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#666666"
                                font.pixelSize: 12
                                Layout.fillWidth: true
                            }
                        }
                    }
                }
                
                // 右下角：其他信息
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: "#ffffff"
                    radius: 10
                    border.color: "#e0e0e0"
                    border.width: 1
                    
                    // 阴影效果
                    Rectangle {
                        anchors.fill: parent
                        anchors.margins: -3
                        color: "transparent"
                        border.color: "#d0d0d0"
                        border.width: 1
                        radius: 13
                        z: -1
                        opacity: 0.2
                    }
                    
                    ColumnLayout {
                        anchors.fill: parent
                        anchors.topMargin: 8
                        anchors.bottomMargin: 12
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        spacing: 8
                        
                        // 标题区域
                        Rectangle {
                            Layout.fillWidth: true
                            height: 30
                            color: "#f8f9fa"
                            radius: 6
                            
                            Label {
                                anchors.left: parent.left
                                anchors.leftMargin: 10
                                anchors.verticalCenter: parent.verticalCenter
                                text: "UDP信息统计"
                                font.bold: true
                                color: "#2c3e50"
                                font.pixelSize: 13
                            }
                        }
                        
                        // UDP信息统计
                        RowLayout {
                            spacing: 12
                            Label {
                                text: "已接收:"
                                color: "#555555"
                                font.pixelSize: 12
                            }
                            Label {
                                id: packetCountLabel
                                text: udpComm.packetCount.toString()
                                color: "#006600"
                                font.bold: true
                                font.pixelSize: 13
                                Layout.preferredWidth: 80
                                horizontalAlignment: Text.AlignRight
                            }
                            Label {
                                text: "条"
                                color: "#555555"
                                font.pixelSize: 12
                            }
                            Label {
                                text: "|"
                                color: "#cccccc"
                            }
                            Label {
                                text: "接收速率:"
                                color: "#555555"
                                font.pixelSize: 12
                            }
                            Label {
                                id: rateLabel
                                text: udpComm.packetsPerSecond.toString()
                                color: "#0066cc"
                                font.bold: true
                                font.pixelSize: 13
                                Layout.preferredWidth: 60
                                horizontalAlignment: Text.AlignRight
                            }
                            Label {
                                text: "条/秒"
                                color: "#555555"
                                font.pixelSize: 12
                            }
                            Item { Layout.fillWidth: true }
                        }
                        
                        // UDP数据包信息
                        RowLayout {
                            spacing: 8
                            Label {
                                text: "数据包信息:"
                                color: "#555555"
                                font.pixelSize: 12
                                Layout.preferredWidth: 80
                            }
                            Label {
                                id: udpPacketInfoLabel
                                text: "最新数据包信息将在这里显示"
                                wrapMode: Label.Wrap
                                color: "#666666"
                                font.pixelSize: 12
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
            console.log("onSpectrumReady - 数据大小:", averagedSpectrum ? averagedSpectrum.length : 0, "minVal:", minVal, "maxVal:", maxVal)
            spectrumData = averagedSpectrum
            spectrumMinVal = minVal
            spectrumMaxVal = maxVal
            spectrumPacketCount = packetCount
            // 强制刷新图表
            spectrumCanvas.requestPaint()
            // 同步刷新预测结果曲线
            predictionCanvas.requestPaint()

            // 如果单次采集窗口处于等待状态，则记录（或跳过）光谱
            if (singleCaptureWaiting && singleSpectrumWindow.visible) {
                // 本次“单次采集”已经接收到的光谱条数 +1
                singleCaptureReceivedCount = singleCaptureReceivedCount + 1

                if (singleCaptureReceivedCount === 1) {
                    // 第 1 条光谱：按照需求只略过、不记录
                    singleSpectrumStatusLabel.text = "已接收到第 1 条光谱数据，已略过，正在等待第 2 条用于记录..."
                    singleSpectrumStatusLabel.color = "#0066cc"
                } else {
                    // 第 2 条光谱：真正记录这一条，然后结束本次等待
                    singleCaptureWaiting = false

                    // 复制一份当前光谱数据，作为这一条记录的独立数据
                    var spectrumCopy = []
                    if (averagedSpectrum && averagedSpectrum.length) {
                        for (var i = 0; i < averagedSpectrum.length; ++i) {
                            spectrumCopy.push(averagedSpectrum[i])
                        }
                    }

                    // 更新矩阵列数（取第一次采集的长度为标准）
                    if (singleSpectrumLength === 0 && spectrumCopy.length > 0) {
                        singleSpectrumLength = spectrumCopy.length
                    }

                    var recordIndex = singleSpectrumRecords.length
                    singleSpectrumRecords.push({
                        time: new Date(),
                        index: recordIndex + 1,
                        spectrum: spectrumCopy,
                        length: spectrumCopy.length,
                        minVal: minVal,
                        maxVal: maxVal,
                        label: singleSpectrumLabelInput.text,
                        moisture: Number(singleSpectrumMoistureInput.text)
                    })

                    // 显式增加计数，触发界面中所有 model 重新计算
                    singleSpectrumRecordCount = singleSpectrumRecordCount + 1

                    singleSpectrumStatusLabel.text = "已成功采集到第 " + (recordIndex + 1) + " 条光谱数据（本次采集使用的是第 2 条光谱）"
                    singleSpectrumStatusLabel.color = "#006600"
                }
            }
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
                
                // 更新预测结果历史（最多保存10个）
                if (!predictionHistory) {
                    predictionHistory = []
                }
                predictionHistory.push(predictionValue)
                // 如果超过10个，移除最旧的数据
                if (predictionHistory.length > 10) {
                    predictionHistory.shift()
                }
                console.log("onPredictionReady - predictionHistory 大小:", predictionHistory.length, "最新值:", predictionValue)
                // 强制刷新预测结果曲线
                predictionCanvas.requestPaint()
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
    property var predictionHistory: []  // 存储预测结果历史（最多10个）

    // 单次光谱采集相关属性
    property bool singleCaptureWaiting: false          // 是否正在等待一条新的光谱
    // 每条记录包含: time（时间）、index（第几次）、spectrum（该次完整光谱数据数组）
    property var singleSpectrumRecords: []
    // 单次采集的光谱长度（列数），用于构建“索引 + 多条光谱”的矩阵表
    property int singleSpectrumLength: 0
    // 已采集的单次光谱条数（专门用于刷新界面）
    property int singleSpectrumRecordCount: 0
    // 当前这次“单次采集”已经接收到的光谱条数（用于跳过第一条，记录第二条）
    property int singleCaptureReceivedCount: 0
    // 当前要进行 CSV 保存/加载操作的记录索引（-1 表示未选择）
    property int csvTargetRecordIndex: -1
    // 从 CSV 导入时暂存的新记录列表，供用户选择覆盖或追加
    property var pendingImportedRecords: []

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
    
    // 单次光谱采集与记录窗口（不包含预测功能，只使用已经进行过黑白校正后的光谱）
    Window {
        id: singleSpectrumWindow
        width: 800
        height: 500
        minimumWidth: 600
        minimumHeight: 400
        title: "单次光谱采集与记录"
        visible: false
        modality: Qt.ApplicationModal

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            FileDialog {
                id: saveCsvDialog
                title: "选择要保存 CSV 的文件路径"
                fileMode: FileDialog.SaveFile
                nameFilters: [ "CSV 文件 (*.csv)", "所有文件 (*)" ]
                onAccepted: {
                    if (csvTargetRecordIndex >= 0 &&
                            csvTargetRecordIndex < singleSpectrumRecords.length) {
                        const rec = singleSpectrumRecords[csvTargetRecordIndex]
                        const ok = spectrumFileManager.saveSpectrumToCsv(rec.spectrum, selectedFile)
                        if (ok) {
                            singleSpectrumStatusLabel.text = "✓ 已将第 " + (csvTargetRecordIndex + 1) + " 条光谱保存到: " + selectedFile
                            singleSpectrumStatusLabel.color = "#006600"
                        } else {
                            singleSpectrumStatusLabel.text = "✗ 保存 CSV 失败，请检查路径权限"
                            singleSpectrumStatusLabel.color = "#cc0000"
                        }
                    }
                    csvTargetRecordIndex = -1
                }
                onRejected: {
                    csvTargetRecordIndex = -1
                }
            }

            FileDialog {
                id: loadCsvDialog
                title: "选择要导入的 CSV 文件"
                fileMode: FileDialog.OpenFile
                nameFilters: [ "CSV 文件 (*.csv)", "所有文件 (*)" ]
                onAccepted: {
                    if (csvTargetRecordIndex >= 0 &&
                            csvTargetRecordIndex < singleSpectrumRecords.length) {
                        const newSpectrum = spectrumFileManager.loadSpectrumFromCsv(selectedFile)
                        if (!newSpectrum || newSpectrum.length === 0) {
                            singleSpectrumStatusLabel.text = "✗ 从 CSV 导入光谱失败或文件为空"
                            singleSpectrumStatusLabel.color = "#cc0000"
                        } else {
                            // 用导入的光谱替换当前记录的光谱，并更新统计信息
                            var minVal = newSpectrum[0]
                            var maxVal = newSpectrum[0]
                            for (var i = 1; i < newSpectrum.length; ++i) {
                                if (newSpectrum[i] < minVal) minVal = newSpectrum[i]
                                if (newSpectrum[i] > maxVal) maxVal = newSpectrum[i]
                            }
                            singleSpectrumRecords[csvTargetRecordIndex].spectrum = newSpectrum
                            singleSpectrumRecords[csvTargetRecordIndex].length = newSpectrum.length
                            singleSpectrumRecords[csvTargetRecordIndex].minVal = minVal
                            singleSpectrumRecords[csvTargetRecordIndex].maxVal = maxVal

                            singleSpectrumStatusLabel.text = "✓ 已从 CSV 导入并更新第 " + (csvTargetRecordIndex + 1) + " 条光谱数据"
                            singleSpectrumStatusLabel.color = "#006600"
                        }
                    }
                    csvTargetRecordIndex = -1
                }
                onRejected: {
                    csvTargetRecordIndex = -1
                }
            }

            FileDialog {
                id: saveAllCsvDialog
                title: "选择要保存全部记录的 CSV 表格路径"
                fileMode: FileDialog.SaveFile
                nameFilters: [ "CSV 文件 (*.csv)", "所有文件 (*)" ]
                onAccepted: {
                    if (singleSpectrumRecordCount <= 0) {
                        singleSpectrumStatusLabel.text = "✗ 当前没有可导出的记录"
                        singleSpectrumStatusLabel.color = "#cc0000"
                        return
                    }
                    // FileDialog 返回的是一个 URL，需要转换为本地文件系统路径
                    var urlStr = saveAllCsvDialog.selectedFile.toString()
                    var path = urlStr
                    if (urlStr.startsWith("file://")) {
                        // 在 Linux 下通常是 file:///home/xxx，去掉前缀得到 /home/xxx
                        path = urlStr.substring(7)
                    }
                    // 如果用户没有手动加 .csv 后缀，则自动补上
                    if (!path.toLowerCase().endsWith(".csv")) {
                        path = path + ".csv"
                    }
                    const ok = spectrumFileManager.saveAllSpectraTableToCsv(singleSpectrumRecords, path)
                    if (ok) {
                        singleSpectrumStatusLabel.text = "✓ 已将全部 " + singleSpectrumRecordCount + " 条记录导出到: " + path
                        singleSpectrumStatusLabel.color = "#006600"
                    } else {
                        singleSpectrumStatusLabel.text = "✗ 导出全部记录到 CSV 失败，请检查路径权限"
                        singleSpectrumStatusLabel.color = "#cc0000"
                    }
                }
            }

            FileDialog {
                id: loadAllCsvDialog
                title: "选择要从中导入全部记录的 CSV 表格"
                fileMode: FileDialog.OpenFile
                nameFilters: [ "CSV 文件 (*.csv)", "所有文件 (*)" ]
                onAccepted: {
                    // FileDialog 返回的是一个 URL，需要转换为本地文件系统路径
                    var urlStr = loadAllCsvDialog.selectedFile.toString()
                    var path = urlStr
                    if (urlStr.startsWith("file://")) {
                        path = urlStr.substring(7)
                    }

                    const recs = spectrumFileManager.loadAllSpectraTableFromCsv(path)
                    if (!recs || recs.length === 0) {
                        singleSpectrumStatusLabel.text = "✗ 从 CSV 导入记录失败或无有效数据"
                        singleSpectrumStatusLabel.color = "#cc0000"
                        return
                    }

                    pendingImportedRecords = recs
                    // 弹出提示对话框，让用户选择覆盖现有记录还是在后面追加
                    importModeDialog.infoText = "从 CSV 读取到 " + recs.length + " 条记录。\n\n" +
                                                "是否覆盖当前已有记录？\n" +
                                                "选择“覆盖导入”将清空现有记录后再导入；\n" +
                                                "选择“追加导入”则会在现有记录之后追加导入的记录。"
                    importModeDialog.open()
                }
            }

            Dialog {
                id: importModeDialog
                title: "导入记录方式选择"
                modal: true
                standardButtons: Dialog.NoButton
                property string infoText: ""

                // 第一步美化：自定义背景为与主界面一致的白色圆角卡片
                background: Rectangle {
                    color: "#ffffff"
                    radius: 10
                    border.color: "#e0e0e0"
                    border.width: 1
                }

                // 第二步美化：自定义遮罩为半透明黑色
                Overlay.modal: Rectangle {
                    color: "#000000"
                    opacity: 0.25
                }

                contentItem: ColumnLayout {
                    spacing: 10
                    anchors.margins: 16

                    Label {
                        text: "导入记录方式选择"
                        font.bold: true
                        font.pixelSize: 14
                        color: "#2c3e50"
                        Layout.fillWidth: true
                    }

                    Label {
                        text: importModeDialog.infoText
                        wrapMode: Label.Wrap
                        color: "#555555"
                        font.pixelSize: 12
                        Layout.fillWidth: true
                    }

                    RowLayout {
                        Layout.alignment: Qt.AlignRight
                        spacing: 8

                        Button {
                            text: "覆盖导入"
                            background: Rectangle {
                                color: parent.pressed ? "#c0392b" : (parent.hovered ? "#e74c3c" : "#e74c3c")
                                radius: 6
                                border.color: "#c0392b"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
                            onClicked: {
                                if (!pendingImportedRecords || pendingImportedRecords.length === 0) {
                                    importModeDialog.close()
                                    return
                                }
                                var recs = pendingImportedRecords
                                // 覆盖模式
                                singleSpectrumRecords = recs
                                singleSpectrumRecordCount = recs.length

                                if (singleSpectrumRecords.length > 0 &&
                                        singleSpectrumRecords[0].length !== undefined) {
                                    singleSpectrumLength = singleSpectrumRecords[0].length
                                }

                                pendingImportedRecords = []
                                singleSpectrumStatusLabel.text = "✓ 已从 CSV 覆盖导入 " + recs.length + " 条记录"
                                singleSpectrumStatusLabel.color = "#006600"
                                importModeDialog.close()
                            }
                        }

                        Button {
                            text: "追加导入"
                            background: Rectangle {
                                color: parent.pressed ? "#16a085" : (parent.hovered ? "#1abc9c" : "#1abc9c")
                                radius: 6
                                border.color: "#16a085"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
                            onClicked: {
                                if (!pendingImportedRecords || pendingImportedRecords.length === 0) {
                                    importModeDialog.close()
                                    return
                                }
                                var recs = pendingImportedRecords
                                // 追加模式
                                for (var i = 0; i < recs.length; ++i) {
                                    singleSpectrumRecords.push(recs[i])
                                }
                                singleSpectrumRecordCount = singleSpectrumRecordCount + recs.length

                                if (singleSpectrumRecords.length > 0 &&
                                        singleSpectrumRecords[0].length !== undefined) {
                                    singleSpectrumLength = singleSpectrumRecords[0].length
                                }

                                pendingImportedRecords = []
                                singleSpectrumStatusLabel.text = "✓ 已从 CSV 追加导入 " + recs.length + " 条记录"
                                singleSpectrumStatusLabel.color = "#006600"
                                importModeDialog.close()
                            }
                        }

                        Button {
                            text: "取消"
                            background: Rectangle {
                                color: parent.pressed ? "#95a5a6" : (parent.hovered ? "#bdc3c7" : "#ecf0f1")
                                radius: 6
                                border.color: "#bdc3c7"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#2c3e50"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 12
                                font.bold: true
                            }
                            onClicked: {
                                pendingImportedRecords = []
                                importModeDialog.close()
                            }
                        }
                    }
                }
            }

            Label {
                text: "功能说明：本窗口仅用于采集单条光谱并记录，不进行预测运算。\n请先在主界面完成黑/白参考采集，并确保已经开始获取光谱数据。"
                wrapMode: Label.Wrap
                color: "#555555"
                Layout.fillWidth: true
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#e0e0e0"
            }

            // 光谱标签与对应水分输入
            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Label {
                    text: "光谱标签:"
                    color: "#555555"
                    Layout.preferredWidth: 60
                }
                TextField {
                    id: singleSpectrumLabelInput
                    placeholderText: "例如: 样品1 / 玉米A"
                    Layout.preferredWidth: 160
                    Layout.fillWidth: true
                    font.pixelSize: 12
                }

                Label {
                    text: "水分含量:"
                    color: "#555555"
                    Layout.preferredWidth: 70
                }
                TextField {
                    id: singleSpectrumMoistureInput
                    placeholderText: "例如: 12.34"
                    Layout.preferredWidth: 100
                    inputMethodHints: Qt.ImhFormattedNumbersOnly
                    font.pixelSize: 12
                }
                Label {
                    text: "%"
                    color: "#555555"
                    Layout.preferredWidth: 12
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    text: singleCaptureWaiting ? "正在等待数据..." : "采集一条新的光谱"
                    enabled: !singleCaptureWaiting
                    Layout.preferredWidth: 180
                    Layout.fillWidth: true
                    background: Rectangle {
                        color: parent.pressed ? "#27ae60" : (parent.hovered ? "#2ecc71" : "#27ae60")
                        radius: 6
                        border.color: "#229954"
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 13
                        font.bold: true
                    }

                    onClicked: {
                        if (!udpComm.receiving && !serialComm.isStarted) {
                            singleSpectrumStatusLabel.text = "✗ 请先在主界面启动“开始获取光谱”（串口/UDP）"
                            singleSpectrumStatusLabel.color = "#cc0000"
                            return
                        }

                        // 启动一次新的“单次采集”：本次将跳过收到的第1条光谱，只记录第2条
                        singleCaptureWaiting = true
                        singleCaptureReceivedCount = 0
                        singleSpectrumStatusLabel.text = "正在等待第 1 条光谱数据（将被略过），随后记录第 2 条..."
                        singleSpectrumStatusLabel.color = "#0066cc"
                    }
                }

                Button {
                    text: "关闭"
                    Layout.preferredWidth: 80
                    background: Rectangle {
                        color: parent.pressed ? "#95a5a6" : (parent.hovered ? "#bdc3c7" : "#ecf0f1")
                        radius: 6
                        border.color: "#bdc3c7"
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#2c3e50"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                    onClicked: {
                        singleCaptureWaiting = false
                        singleSpectrumWindow.close()
                    }
                }
            }

            Label {
                id: singleSpectrumStatusLabel
                text: "尚未采集单次光谱。"
                color: "#666666"
                font.pixelSize: 12
                Layout.fillWidth: true
                wrapMode: Label.Wrap
            }

            Rectangle {
                Layout.fillWidth: true
                height: 1
                color: "#e0e0e0"
            }

            Label {
                text: "已记录的单次光谱（时间与序号列表）："
                font.bold: true
                color: "#34495e"
                Layout.fillWidth: true
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: 8

                Button {
                    text: "导出全部到 CSV（表格）"
                    Layout.preferredWidth: 200
                    background: Rectangle {
                        color: parent.pressed ? "#2980b9" : (parent.hovered ? "#3498db" : "#3498db")
                        radius: 6
                        border.color: "#2980b9"
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                    enabled: singleSpectrumRecordCount > 0
                    onClicked: {
                        if (singleSpectrumRecordCount <= 0) {
                            singleSpectrumStatusLabel.text = "当前没有可导出的记录"
                            singleSpectrumStatusLabel.color = "#cc0000"
                            return
                        }
                        saveAllCsvDialog.open()
                    }
                }

                Button {
                    text: "从 CSV 导入全部记录"
                    Layout.preferredWidth: 200
                    background: Rectangle {
                        color: parent.pressed ? "#16a085" : (parent.hovered ? "#1abc9c" : "#1abc9c")
                        radius: 6
                        border.color: "#16a085"
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#ffffff"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                    onClicked: {
                        loadAllCsvDialog.open()
                    }
                }

                Button {
                    text: "清空全部记录"
                    Layout.preferredWidth: 120
                    background: Rectangle {
                        color: parent.pressed ? "#7f8c8d" : (parent.hovered ? "#95a5a6" : "#bdc3c7")
                        radius: 6
                        border.color: "#7f8c8d"
                        border.width: 1
                    }
                    contentItem: Text {
                        text: parent.text
                        color: "#2c3e50"
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        font.pixelSize: 12
                        font.bold: true
                    }
                    enabled: singleSpectrumRecordCount > 0
                    onClicked: {
                        singleSpectrumRecords = []
                        singleSpectrumRecordCount = 0
                        singleSpectrumStatusLabel.text = "已清空全部单次采集记录"
                        singleSpectrumStatusLabel.color = "#666666"
                    }
                }

                Item { Layout.fillWidth: true }
            }

            ListView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                // 使用单独的计数属性触发 model 更新
                model: singleSpectrumRecordCount

                delegate: Rectangle {
                    width: ListView.view.width
                    height: 32
                    color: index % 2 === 0 ? "#ffffff" : "#f8f9fa"

                    RowLayout {
                        anchors.fill: parent
                        anchors.leftMargin: 8
                        anchors.rightMargin: 8

                        Label {
                            text: "记录 " + (index + 1)
                            color: "#2c3e50"
                            font.bold: true
                        }
                        RowLayout {
                            spacing: 4
                            Layout.preferredWidth: 170

                            Label {
                                text: "标签:"
                                color: "#555555"
                            }
                            TextField {
                                id: recordLabelEditor
                                text: singleSpectrumRecords[index].label
                                placeholderText: "(可编辑标签)"
                                font.pixelSize: 11
                                Layout.fillWidth: true
                                onEditingFinished: {
                                    singleSpectrumRecords[index].label = text
                                }
                            }
                        }
                        Label {
                            // 采集时间
                            text: Qt.formatDateTime(singleSpectrumRecords[index].time,
                                                     "yyyy-MM-dd hh:mm:ss")
                            color: "#555555"
                            Layout.preferredWidth: 130
                        }
                        Label {
                            text: "长度: " + singleSpectrumRecords[index].length
                            color: "#555555"
                            Layout.preferredWidth: 90
                        }
                        Label {
                            text: "最小值: " + Number(singleSpectrumRecords[index].minVal).toFixed(2)
                            color: "#555555"
                            Layout.preferredWidth: 110
                        }
                        Label {
                            text: "最大值: " + Number(singleSpectrumRecords[index].maxVal).toFixed(2)
                            color: "#555555"
                            Layout.preferredWidth: 110
                        }
                        RowLayout {
                            spacing: 4
                            Layout.preferredWidth: 140

                            Label {
                                text: "水分:"
                                color: "#555555"
                            }
                            TextField {
                                id: recordMoistureEditor
                                text: isNaN(singleSpectrumRecords[index].moisture)
                                      ? ""
                                      : Number(singleSpectrumRecords[index].moisture).toFixed(2)
                                placeholderText: "12.34"
                                font.pixelSize: 11
                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                Layout.fillWidth: true
                                onEditingFinished: {
                                    var v = Number(text)
                                    if (!isNaN(v)) {
                                        singleSpectrumRecords[index].moisture = v
                                    }
                                }
                            }
                            Label {
                                text: "%"
                                color: "#555555"
                            }
                        }
                        Button {
                            text: "删除"
                            Layout.preferredWidth: 60
                            background: Rectangle {
                                color: parent.pressed ? "#c0392b" : (parent.hovered ? "#e74c3c" : "#e74c3c")
                                radius: 6
                                border.color: "#c0392b"
                                border.width: 1
                            }
                            contentItem: Text {
                                text: parent.text
                                color: "#ffffff"
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: 11
                                font.bold: true
                            }
                            onClicked: {
                                if (singleSpectrumRecordCount <= 0) return
                                // 删除当前这一条记录
                                singleSpectrumRecords.splice(index, 1)
                                singleSpectrumRecordCount = singleSpectrumRecordCount - 1
                                singleSpectrumStatusLabel.text = "已删除第 " + (index + 1) + " 条记录"
                                singleSpectrumStatusLabel.color = "#666666"
                            }
                        }
                        Item { Layout.fillWidth: true }
                    }
                }

                ScrollBar.vertical: ScrollBar { }
            }
        }
    }
}


