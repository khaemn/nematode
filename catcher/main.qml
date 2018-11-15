import QtQuick 2.5
import QtQuick.Controls 1.4
import QtQuick.Layouts 1.2

ApplicationWindow {
    id: root

    visible: true
    width: 800
    height: 200
    title: qsTr("Nematode")

    readonly property int _zoneWidth: 100

    function init() {

    }

    MouseArea {
        id: _area

        anchors.fill: parent
    }

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

    Canvas {
        id: _canvas
        anchors.fill: parent
    }

    Ship {
        anchors.centerIn: _launchBay
    }

    Cannon {
        anchors.centerIn: _area
    }
}
