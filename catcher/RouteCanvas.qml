import QtQuick 2.7

Canvas {
    id: root

    readonly property string action_line: "line"
    readonly property string action_render_predictions: "render_predictions"
    readonly property string action_render_blasts: "render_blasts"
    readonly property string action_render_route: "render_route"
    readonly property string action_clear: "clear"

    property Cannon cannon: Cannon{}
    property Ship ship: Ship{}

    property point prev: "0,0"
    property point curr: "0,0"
    property var actions: []

    property alias next: _next
    property alias future: _future
    property alias blast: _blast

    property int blastRadius: 20
    readonly property int routePointSize: 10
    readonly property int predictionPointSize: 10

    property var route: [[200,200],[210,200],[250,200],[280,200]]
    property var predictionPoints: [[100,100],[200,200],[100,200],[300,500]]
    property var blastPoints: [[200,100],[300,200],[200,300],[500,100]]

    function doAction(_action, _x, _y) {
        actions.push([_action]);
        
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

    // TODO: eliminate copypasta
    function _render_predictions() {
        var ctx = getContext("2d");
        for (var i = 1; i < predictionPoints.length; i++) {
            ctx.drawImage("img/prediction.png",
                          predictionPoints[i][0] - predictionPointSize/2,
                          predictionPoints[i][1] - predictionPointSize/2,
                          predictionPointSize,
                          predictionPointSize);
        }
    }

    function _render_route() {
        var ctx = getContext("2d");
        for (var i = 1; i < route.length; i++) {
            ctx.drawImage("img/routepoint.png",
                          route[i][0],
                          route[i][1],
                          routePointSize,
                          routePointSize);
        }
    }

    function _render_blasts() {
        var ctx = getContext("2d");
        for (var i = 1; i < blastPoints.length; i++) {
            ctx.drawImage("img/blast.png",
                          blastPoints[i][0],
                          blastPoints[i][1],
                          blastRadius * 2,
                          blastRadius * 2);
        }
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
        for (var i = 0; i < actions.length; i++) {

            var action = actions[i];

            if (action == action_render_predictions) {
                _render_predictions();
            }
            if (action == action_render_blasts) {
                _render_blasts();
            }
            if (action == action_render_route) {
                _render_route();
            }
            if (action == action_line) {
                _drawLine();
            }
            if (action == action_clear) {
                _clear();
            }
        }
        actions = [];
    }
}
