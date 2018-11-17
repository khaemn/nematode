import QtQuick 2.7

Item {
    id: root

    property real health: 1.0
    property real fuel: 1.0
    property real course: 0.0
    property int size: 40
    property int hitRadius: 5

    property int animationInterval: 300

    width: size
    height: size


    Image {
        source: health > 0 ? "img/ship.png" : "img/dead.png"

        anchors.centerIn: parent

        width: parent.width
        height: parent.height
        rotation: 45 + root.course // +45 because of rotation in original image
    }

    LinearIndicator {
        id: _healthIndicator
        value: root.health
    }

    LinearIndicator {
        id: _fuelIndicator

        anchors.top: _healthIndicator.bottom
        anchors.topMargin: 2

        color: "transparent"
        fillColor: "cyan"
        value: root.fuel
    }

    Rectangle {
        id: hitArea
        color: "magenta"

        anchors.centerIn: parent

        height: root.hitRadius * 2
        width: height
        radius: width / 2
        opacity: 0.3
    }

    Behavior on x {
        NumberAnimation { duration: animationInterval }
    }
    Behavior on y {
        NumberAnimation { duration: animationInterval }
    }
    Behavior on rotation {
        RotationAnimator { duration: animationInterval / 2 }
    }
}
