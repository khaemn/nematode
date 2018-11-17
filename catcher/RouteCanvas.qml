import QtQuick 2.7

Canvas {
    id: root

    readonly property string _action_line: "line"
    readonly property string _action_clear: "clear"

    property Cannon cannon: Cannon{}
    property Ship ship: Ship{}

    property point prev: "0,0"
    property point curr: "0,0"
    property string action: ""

    property alias next: _next
    property alias future: _future
    property alias blast: _blast

    function doAction(_action, _x, _y) {
        action = _action;
        
        curr.x = _x;
        curr.y = _y;
        
        root.requestPaint();
        
        prev.x = _x;
        prev.y = _y;
    }

    function _drawLine() {
        var ctx = getContext("2d")
        ctx.strokeStyle = "yellow";
        ctx.lineWidth = 2;
        
        // Initial case when user has only just started drawing
        if (prev.x === 0 && prev.y === 0) {
            if (curr.x > 0 && curr.y > 0)
                ctx.moveTo(curr.x, curr.y)
            return;
        }
        
        ctx.lineTo(curr.x, curr.y);
        ctx.stroke();
    }
    
    function _clear() {
        var ctx = getContext("2d")
        ctx.reset();
    }

    Marker {
        id: _next
        visible: false
    }

    Marker {
        id: _future
        visible: false
        opacity: 0.3
    }

    Marker {
        id: _blast
        visible: false

        size: 40
        color: "yellow"
        opacity: 1.0

        z: parent.z + 1
    }

    onPaint: {
        if (action === _action_line) {
            _drawLine();
        }
        if (action === _action_clear) {
            _clear();
        }
    }
}
