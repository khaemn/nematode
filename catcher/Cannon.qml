import QtQuick 2.7

Item {
    id: root

    property int size: 40

    width: size
    height: size

    Image {
        source: "cannon.png"

        anchors.centerIn: parent

        width: parent.width
        height: parent.height
    }
}
