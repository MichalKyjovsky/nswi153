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
import { LayoutGraph } from './Common';

const initialNodes: Node[] = [
    { id: '1', data: { label: 'Node 1' }, position: { x: 5, y: 5 } },
    { id: '2', data: { label: 'Node 2' }, position: { x: 5, y: 100 } },
];

const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2' },
];

const fitViewOptions: FitViewOptions = {
    padding: 0.2
}

function VisualisationContent() {
    const [websiteRecordFilter, setWebsiteRecordFilter] = React.useState<number | undefined>(undefined);
    const [websiteRecords, setWebsiteRecords] = React.useState<WebsiteRecordForSelect[]>([]);

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

    const visualizer = new GraphVisualizer(manager.getGraph());
    visualizer.layout();
    console.log(visualizer.graph);
    const visualizedGraph = visualizer.getGraph(800, 600);

    const [nodes, setNodes] = React.useState<Node[]>(visualizedGraph.nodes);
    const [edges, setEdges] = React.useState<Edge[]>(visualizedGraph.edges);

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
                            variant="h6"
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
                    <Container maxWidth={false} sx={{ mt: 2, mb: 2, minWidth: 800, maxWidth: 1600, height: 600 }}>
                        <ReactFlow
                            nodes={nodes}
                            edges={edges}
                            onNodesChange={onNodesChange}
                            onEdgesChange={onEdgesChange}
                            onConnect={onConnect}
                            fitView
                            fitViewOptions={fitViewOptions}
                        />
                    </Container>
                </Container>
            </Box>
        </Box>
    );
}

export default function Visualisation() {
    return <VisualisationContent />;
}
