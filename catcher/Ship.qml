import QtQuick 2.7

Item {
    id: root

    property int size: 40
    property int animationInterval: 0

    width: size
    height: size

    Image {
        source: "ship.png"

        anchors.centerIn: parent

        width: parent.width
        height: parent.height
        rotation: 45 // because of rotation in original image
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
