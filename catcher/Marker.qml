import QtQuick 2.7

Rectangle {
    id: root

    property int size: 20
    property point centerPoint: "0,0"

    width: size
    height: size
    radius: width / 2
    border.width: 1
    border.color: "magenta"
    color: "red"
    opacity: 0.5
    x: centerPoint.x - width / 2
    y: centerPoint.y - height / 2
}
