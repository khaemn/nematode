
import QtQuick 2.5
import QtQuick.Controls 1.4

ApplicationWindow {
    id: root

    visible: true

    width: 800
    height: 800
    maximumHeight: height
    maximumWidth: width
    minimumHeight: height
    minimumWidth: width

    title: qsTr("Nematode")
    color: "darkgrey"

    readonly property int _zoneWidth: 100
    readonly property int animationInterval: 500

    readonly property var engine: gameEngine // context property

    property bool isGameInProgress: false

    function init() {
        _canvas.doAction("clear");
        _ship.anchors.centerIn = _launchBay
        _ship.anchors.centerIn = undefined
        _ship.course = 0;
        _ship.health = 1.0
    }

    function startGame() {
        engine.initFlight();
        _playTimer.start();
        isGameInProgress = true;
    }

    function stopGame() {
        isGameInProgress = false;
        _playTimer.stop();
        _canvas.next.visible = false;
        _canvas.future.visible = false;
        _canvas.blast.visible = false;
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

            color: "darkgreen"
        }

        RouteCanvas {
            id: _canvas

            anchors.fill: parent
            cannon: _cannon
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

            onPressed: {
                stopGame();
                init();
            }

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

        Marker {
            // Workaround to display blast over the ship
            id: _blast
            visible: _canvas.blast.visible
            centerPoint: _canvas.blast.centerPoint
            size: _canvas.blast.size
            color: _canvas.blast.color
            opacity: 0.6
        }

        Cannon {
            id: _cannon
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
            enabled: !_playTimer.running && !isGameInProgress

            onClicked: {
                startGame();
            }
        }
        Button {
            id: _pauseButton
            width: 100
            text: "Pause"
            enabled: _playTimer.running && isGameInProgress
            onClicked: {
                _playTimer.stop();
            }
        }
        Button {
            id: _stepForward
            width: 100
            text: "step >"
            enabled: !_playTimer.running
            onClicked: {
                if (isGameInProgress) {
                    engine.tick();
                } else {
                    startGame();
                    _playTimer.stop();
                }
            }
        }
        Button {
            id: _resumeButton
            width: 100
            text: "Resume"
            enabled: !_playTimer.running && isGameInProgress
            onClicked: {
                _playTimer.start();
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

        onUpdateShip: {
            _ship.x = newX - _ship.width / 2;
            _ship.y = newY - _ship.height / 2;
            _ship.course = newRotation;
            _ship.health = newHealth;
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
            stopGame();
        }

        onShowNextPointAt: {
            _canvas.next.centerPoint.x = newX;
            _canvas.next.centerPoint.y = newY;
            _canvas.next.visible = true;
        }

        onShowFuturePointAt: {
            _canvas.future.centerPoint.x = newX;
            _canvas.future.centerPoint.y = newY;
            _canvas.future.visible = true;
        }

        onShowBlastAt: {
            _canvas.blast.centerPoint.x = newX;
            _canvas.blast.centerPoint.y = newY;
            _canvas.blast.visible = true;
            _canvas.blast.size = newRadius * 2;
        }
    }
}
