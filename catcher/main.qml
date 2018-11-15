import QtQuick 2.5
import QtQuick.Controls 1.4

ApplicationWindow {
    id: root

    visible: true
    width: 800
    height: 200
    title: qsTr("Nematode")
    color: "darkgrey"

    readonly property int _zoneWidth: 100
    readonly property int animationInterval: 300

    readonly property var engine: gameEngine // context property

    function init() {
        // TODO: impl!
    }

    Item {
        id: _playground

        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right

        anchors.bottom: _toolbar.top

        Rectangle {
            id: _launchBay

            // TODO: reanchor to a center point or given rect coords.
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: _zoneWidth

            color: "blue"
        }

        Rectangle {
            id: _landingZone

            // TODO: reanchor to a center point or given rect coords.
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom

            width: _zoneWidth

            color: "red"
        }

        RouteCanvas {
            id: _canvas
        }

        MouseArea {
            id: _area

            property int inputDivider: 0
            property int inputDividerThreshold: 5

            property bool isEditingInProgress: false

            anchors.fill: parent

            onPositionChanged: {
                if (!isEditingInProgress) {
                    // Making immediate reaction on the first move.
                    isEditingInProgress = true;
                    inputDivider = inputDividerThreshold;
                }

                if (++inputDivider < inputDividerThreshold) {
                    return;
                }
                inputDivider = 0;
                _canvas.doAction("line", mouseX, mouseY);
                console.log(mouseX, mouseY);
                engine.addRoutePoint(mouseX, mouseY);
            }

            onCanceled: pressed

            onPressed: { _canvas.doAction("clear"); }

            onReleased: {
                isEditingInProgress = false;
                engine.routeEditingCompleted();
            }

            onWidthChanged: {
                engine.areaSizeChanged(width, height);
            }
            onHeightChanged:  {
                engine.areaSizeChanged(width, height);
            }
        }

        Ship {
            id: _ship
            x: 10
            y: 10

            animationInterval: root.animationInterval
        }

        Cannon {
            anchors.centerIn: _area
        }
    }

    Row {
        id: _toolbar

        anchors.left: parent.left
        anchors.right: parent.right
        anchors.bottom: parent.bottom

        height: _playButton.height

        Button {
            id: _playButton
            width: 100
            text: "Play"
            enabled: !_playTimer.running

            onClicked: {
                _playTimer.start();
            }
        }
        Button {
            id: _pauseButton
            width: 100
            text: "Pause"
            enabled: _playTimer.running
            onClicked: {
                _playTimer.stop();
            }
        }
    }

    Timer {
        // ! idiotic solution. move to Python side.
        id: _playTimer
        interval: animationInterval

        running: false
        repeat: true

        onTriggered: {
            engine.tick();
        }
    }

    Connections {
        target: gameEngine

        onMoveShipTo: {
            _ship.x = newX - _ship.width / 2;
            _ship.y = newY - _ship.height / 2;
            _ship.rotation = newRotation;
            gameEngine.log("\nShip moved to:  ("
                           + newX + ":" + newY + "|" + newRotation + ")"
                           + "  --->  "
                           + (_ship.x + _ship.width / 2)
                           + ":"
                           + (_ship.y + _ship.height / 2)
                           + "|"
                           + _ship.rotation
                           + "\n");
        }

        onStopPlay: {
            _playTimer.stop();
        }
    }
}
