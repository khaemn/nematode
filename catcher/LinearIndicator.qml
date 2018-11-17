import QtQuick 2.7

Rectangle {
    id: root
    
    property real value: 0.5
    property alias fillColor: _fill.color
    
    anchors.left: parent.left
    anchors.right: parent.right
    anchors.top: parent.top
    height: 3
    color: "red"
    
    Rectangle {
        id: _fill
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: parent.width * value
        
        color: "lightgreen"
    }
}
