import * as React from 'react';
import ReactFlow, {
    addEdge,
    FitViewOptions,
    applyNodeChanges,
    applyEdgeChanges,
    Node,
    Edge,
    NodeChange,
    EdgeChange,
    Connection
} from 'react-flow-renderer';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import ApiManager, { WebsiteRecordForSelect } from './ApiManager';
import GraphVisualizer from './GraphVisualizer';
import { Button, Stack } from '@mui/material';

const fitViewOptions: FitViewOptions = {
    padding: 0.2
}

function VisualisationContent() {
    const [websiteRecordFilter, setWebsiteRecordFilter] = React.useState<number | undefined>(undefined);
    const [websiteRecords, setWebsiteRecords] = React.useState<WebsiteRecordForSelect[]>([]);
    const [selectedNode, setSelectedNode] = React.useState<Node | null>(null);

    const manager = React.useMemo(() => new ApiManager(), []);

    const getRecords = React.useCallback(async () => {
        const response = await manager.listRecords();
        setWebsiteRecords(response ?? []);
    }, [manager]);

    const noFilter = -1;

    React.useEffect(() => {
        getRecords();
    }, [getRecords]);

    const handleWebsiteRecordFilter = (event: SelectChangeEvent<number | undefined>) => {
        const value = event.target.value;
        setWebsiteRecordFilter(value === undefined || value === noFilter ? undefined : Number(value));
    };

    const [nodes, setNodes] = React.useState<Node[]>([]);
    const [edges, setEdges] = React.useState<Edge[]>([]);

    const getGraph = React.useCallback(async (records: number | undefined) => {
        setSelectedNode(null);
        if (records !== undefined) {
            const graph = await manager.getGraph(records.toString());
            if (graph !== null) {
                const visualizer = new GraphVisualizer(graph);
                visualizer.layout();
                const visualizedGraph = visualizer.getGraph(800, 600);
                setNodes(visualizedGraph.nodes);
                setEdges(visualizedGraph.edges);
                return;
            }
        }
        setNodes([]);
        setEdges([]);
    }, [setNodes, setEdges, manager]);

    React.useEffect(() => {
        getGraph(websiteRecordFilter);
    }, [getGraph, websiteRecordFilter]);

    const onNodesChange = React.useCallback(
        (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
        [setNodes]
    );
    const onEdgesChange = React.useCallback(
        (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
        [setEdges]
    );
    const onConnect = React.useCallback(
        (connection: Connection) => setEdges((eds) => addEdge(connection, eds)),
        [setEdges]
    );

    const onNodeDoubleClick = React.useCallback((event: React.MouseEvent, node: Node) => {
        setSelectedNode(node);
    }, [setSelectedNode]);

    return (
        <Box sx={{ display: 'flex' }}>
            <Box
                component="main"
                sx={{
                    backgroundColor: (theme) => theme.palette.grey[100],
                    flexGrow: 1,
                    //height: '100vh',
                    overflow: 'auto',
                }}
            >
                <Container maxWidth={false} sx={{ mt: 2, mb: 2, minWidth: 800, maxWidth: 1600 }}>
                    <Toolbar
                        sx={{
                            pl: { sm: 2 },
                            pr: { xs: 1, sm: 1 },
                        }}
                    >
                        <Typography
                            sx={{ flex: '1 1 100%' }}
                            variant="h5"
                            id="tableTitle"
                            component="h1"
                            color="primary"
                        >
                            Visualisation
                        </Typography>
                        <FormControl variant="standard" sx={{ m: 1, minWidth: 250 }}>
                            <InputLabel id="record-select-label">Website record filter</InputLabel>
                            <Select
                                labelId="record-select-label"
                                id="record-select"
                                value={websiteRecordFilter ?? noFilter}
                                onChange={handleWebsiteRecordFilter}
                                label="Website record filter"
                            >
                                <MenuItem value={-1}>
                                    <em>None</em>
                                </MenuItem>
                                {
                                    websiteRecords.map((rec: WebsiteRecordForSelect, index: number) =>
                                        <MenuItem value={rec.pk} key={`select-item-${index}`}>{rec.label}</MenuItem>
                                    )
                                }
                            </Select>
                        </FormControl>
                    </Toolbar>
                    <Container maxWidth={false} sx={{ mt: 2, mb: 2, minWidth: 800, maxWidth: 1600, height: 600, padding: 0 }}>
                        <div style={{ display: 'flex', height: '100%' }}>
                            <div style={{ flex: '1 1 100%' }}>
                                <ReactFlow
                                    nodes={nodes}
                                    edges={edges}
                                    onNodesChange={onNodesChange}
                                    onEdgesChange={onEdgesChange}
                                    onConnect={onConnect}
                                    onNodeDoubleClick={onNodeDoubleClick}
                                    fitView
                                    fitViewOptions={fitViewOptions}
                                />
                            </div>
                            <div style={{ flexBasis: 'auto', width: 250 }}>
                                <Stack direction={'column'} spacing={1}>
                                    <Typography
                                        variant="h6"
                                        color="primary"
                                    >
                                        Node details
                                    </Typography>
                                    {
                                        selectedNode ? (
                                            <React.Fragment>
                                                <Typography
                                                    variant="subtitle1"
                                                    color="primary"
                                                >
                                                    URL
                                                </Typography>
                                                <Typography variant="body1"> {selectedNode.data.url}</Typography>
                                                {selectedNode.data.crawlTime && selectedNode.data.crawlTime.trim() !== "" && (
                                                    <React.Fragment>
                                                        <Typography
                                                            variant="subtitle1"
                                                            color="primary"
                                                        >
                                                            Crawl time
                                                        </Typography>
                                                        <Typography variant="body1"> {selectedNode.data.crawlTime}</Typography>
                                                    </React.Fragment>
                                                )}
                                                {(selectedNode.data.crawlTime && selectedNode.data.crawlTime.trim() !== "")
                                                    ? <Button variant="contained" >Crawl {websiteRecords.filter(rec => rec.pk === websiteRecordFilter).join()} again</Button>
                                                    : <Button variant="contained">Create new website record</Button>}
                                            </React.Fragment>
                                        ) : (<Typography variant="body1">No selected item</Typography>)}
                                </Stack>
                            </div>
                        </div>
                    </Container>
                </Container>
            </Box>
        </Box>
    );
}

export default function Visualisation() {
    return <VisualisationContent />;
}
