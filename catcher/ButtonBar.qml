import QtQuick 2.5
import QtQuick.Controls 1.4

Row {
    id: _toolbar
    
    property Timer playTimer
    property bool isGameInProgress
    property var engine
    property alias course: courseIndicator.rotation
    property var startGameCallback: function(){}

    readonly property int minInterval: 100
    readonly property int maxInterval: 2000

    Button {
        id: _playButton
        width: 100
        height: parent.height
        text: "Play"
        enabled: !playTimer.running && !isGameInProgress
        
        onClicked: {
            startGameCallback();
        }
    }
    Button {
        id: _pauseButton
        width: 100
        height: parent.height
        text: "Pause"
        enabled: playTimer.running && isGameInProgress
        onClicked: {
            playTimer.stop();
        }
    }
    Button {
        id: _stepForward
        width: 100
        height: parent.height
        text: "step >"
        enabled: !playTimer.running
        onClicked: {
            if (isGameInProgress) {
                engine.tick();
            } else {
                startGameCallback();
                playTimer.stop();
            }
        }
    }
    Button {
        id: _resumeButton
        width: 100
        height: parent.height
        text: "Resume"
        enabled: !playTimer.running && isGameInProgress
        onClicked: {
            playTimer.start();
        }
    }
    Button {
        id: _fasterButton
        width: 100
        height: parent.height
        text: "Faster"
        enabled: playTimer.interval > minInterval
        onClicked: {
            playTimer.interval = Math.max(minInterval, playTimer.interval - 100)
        }
    }
    Button {
        id: _slowerButton
        width: 100
        height: parent.height
        enabled: playTimer.interval < maxInterval
        text: "Slower"
        onClicked: {
            playTimer.interval = Math.min(maxInterval, playTimer.interval + 100)
        }
    }
    Rectangle {
        id: courseIndicator
        height: 30
        width: 30
        anchors.verticalCenter: parent.verticalCenter
        color: "transparent"
        border.width: 2
        border.color: "black"

        Rectangle {
            anchors.right: courseIndicator.right
            anchors.verticalCenter: parent.verticalCenter
            height: 2
            width: parent.width / 1.5
            color: "red"
        }
    }
    Button {
        id: _saveRouteButton
        width: 100
        height: parent.height
        text: "Save Route"
        onClicked: {
            engine.saveRoute();
        }
    }
    
}
