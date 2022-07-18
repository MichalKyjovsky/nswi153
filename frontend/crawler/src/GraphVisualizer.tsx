import {
    Node,
    Edge,
    MarkerType
} from 'react-flow-renderer';
import { LayoutGraph, LayoutEdge, LayoutNode } from './Common';

export default class GraphLayoutRenderer {
    graph: LayoutGraph;
    iterations = 500;
    maxRepulsiveForceDistance = 6;
    k = 2;
    c = 0.01;
    maxVertexMovement = 0.5;

    constructor(graph: LayoutGraph) {
        this.graph = graph;
    }

    layout() {
        this.layoutPrepare();
        for (var i = 0; i < this.iterations; i++) {
            this.layoutIteration();
        }
        this.layoutCalcBounds();
    }

    layoutPrepare() {
        for (var i = 0; i < this.graph.nodes.length; i++) {
            var node = this.graph.nodes[i];
            node.layoutPosX = 0;
            node.layoutPosY = 0;
            node.layoutForceX = 0;
            node.layoutForceY = 0;
        }
    }

    layoutCalcBounds() {
        var minx = Infinity, maxx = -Infinity, miny = Infinity, maxy = -Infinity;

        for (var i = 0; i < this.graph.nodes.length; i++) {
            var x = this.graph.nodes[i].layoutPosX;
            var y = this.graph.nodes[i].layoutPosY;

            if (x > maxx) maxx = x;
            if (x < minx) minx = x;
            if (y > maxy) maxy = y;
            if (y < miny) miny = y;
        }

        this.graph.layoutMinX = minx;
        this.graph.layoutMaxX = maxx;
        this.graph.layoutMinY = miny;
        this.graph.layoutMaxY = maxy;
    }

    layoutIteration() {
        // Forces on nodes due to node-node repulsions
        for (let i = 0; i < this.graph.nodes.length; i++) {
            var node1 = this.graph.nodes[i];
            for (var j = i + 1; j < this.graph.nodes.length; j++) {
                var node2 = this.graph.nodes[j];
                this.layoutRepulsive(node1, node2);
            }
        }
        // Forces on nodes due to edge attractions
        for (let i = 0; i < this.graph.edges.length; i++) {
            var edge = this.graph.edges[i];
            this.layoutAttractive(edge);
        }

        // Move by the given force
        for (let i = 0; i < this.graph.nodes.length; i++) {
            var node = this.graph.nodes[i];
            var xmove = this.c * node.layoutForceX;
            var ymove = this.c * node.layoutForceY;

            var max = this.maxVertexMovement;
            if (xmove > max) xmove = max;
            if (xmove < -max) xmove = -max;
            if (ymove > max) ymove = max;
            if (ymove < -max) ymove = -max;

            node.layoutPosX += xmove;
            node.layoutPosY += ymove;
            node.layoutForceX = 0;
            node.layoutForceY = 0;
        }
    }

    layoutRepulsive(node1: LayoutNode, node2: LayoutNode) {
        var dx = node2.layoutPosX - node1.layoutPosX;
        var dy = node2.layoutPosY - node1.layoutPosY;
        var d2 = dx * dx + dy * dy;
        if (d2 < 0.01) {
            dx = 0.1 * Math.random() + 0.1;
            dy = 0.1 * Math.random() + 0.1;
            d2 = dx * dx + dy * dy;
        }
        var d = Math.sqrt(d2);
        if (d < this.maxRepulsiveForceDistance) {
            var repulsiveForce = this.k * this.k / d;
            node2.layoutForceX += repulsiveForce * dx / d;
            node2.layoutForceY += repulsiveForce * dy / d;
            node1.layoutForceX -= repulsiveForce * dx / d;
            node1.layoutForceY -= repulsiveForce * dy / d;
        }
    }

    layoutAttractive(edge: LayoutEdge) {
        var node1 = edge.source;
        var node2 = edge.target;

        var dx = node2.layoutPosX - node1.layoutPosX;
        var dy = node2.layoutPosY - node1.layoutPosY;
        var d2 = dx * dx + dy * dy;
        if (d2 < 0.01) {
            dx = 0.1 * Math.random() + 0.1;
            dy = 0.1 * Math.random() + 0.1;
            d2 = dx * dx + dy * dy;
        }
        var d = Math.sqrt(d2);
        if (d > this.maxRepulsiveForceDistance) {
            d = this.maxRepulsiveForceDistance;
            d2 = d * d;
        }
        var attractiveForce = (d2 - this.k * this.k) / this.k;
        if (edge.weight === undefined || edge.weight < 1) edge.weight = 1;
        attractiveForce *= Math.log(edge.weight) * 0.5 + 1;

        node2.layoutForceX -= attractiveForce * dx / d;
        node2.layoutForceY -= attractiveForce * dy / d;
        node1.layoutForceX += attractiveForce * dx / d;
        node1.layoutForceY += attractiveForce * dy / d;
    }

    translate(node: LayoutNode, factorX: number, factorY: number): { x: number, y: number } {
        return {
            x: (node.layoutPosX - this.graph.layoutMinX) * factorX,
            y: (node.layoutPosY - this.graph.layoutMinY) * factorY
        };
    }

    getGraph(viewWidth: number, viewHeight: number): { nodes: Node[], edges: Edge[] } {
        const factorX = (viewWidth) / (this.graph.layoutMaxX - this.graph.layoutMinX);
        const factorY = (viewHeight) / (this.graph.layoutMaxY - this.graph.layoutMinY);

        const nodes = this.graph.nodes.map(node => ({ id: node.id, data: { ...node.data, label: node.data.url }, position: this.translate(node, factorX, factorY) }))

        const edges: Edge[] = this.graph.edges.map(edge => ({ id: `e${edge.source.id}-${edge.target.id}`, source: edge.source.id, target: edge.target.id, markerEnd: { type: MarkerType.ArrowClosed, color: 'black' } }))

        return { nodes, edges };
    }
}