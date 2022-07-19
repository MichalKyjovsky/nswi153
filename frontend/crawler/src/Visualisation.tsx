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
import Radio from '@mui/material/Radio';
import RadioGroup from '@mui/material/RadioGroup';
import FormControlLabel from '@mui/material/FormControlLabel';
import FormLabel from '@mui/material/FormLabel';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import Switch from '@mui/material/Switch';
import CircularProgress from '@mui/material/CircularProgress';
import ApiManager, { WebsiteRecordForSelect } from './ApiManager';
import GraphVisualizer from './GraphVisualizer';
import { Button, Stack } from '@mui/material';
import NewSiteModal from './EditSiteModal';
import { WebsiteRecord, emptyWebsiteRecord } from "./Common";

const fitViewOptions: FitViewOptions = {
    padding: 0.2
}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
    props,
    ref,
) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

type Severity = "info" | "success" | "warning" | "error";

function VisualisationContent() {
    const [websiteRecordFilter, setWebsiteRecordFilter] = React.useState<number | undefined>(undefined);
    const [websiteRecords, setWebsiteRecords] = React.useState<WebsiteRecordForSelect[]>([]);
    const [selectedNode, setSelectedNode] = React.useState<Node | null>(null);
    const [graphView, setGraphView] = React.useState("website");
    const [editModalOpen, setEditModalOpen] = React.useState(false);
    const [editedRecord, setEditedRecord] = React.useState<WebsiteRecord>(emptyWebsiteRecord());
    const [notificationOpen, setNotificationOpen] = React.useState(false);
    const [notificationSeverity, setNotificationSeverity] = React.useState<Severity>("info");
    const [notificationMessage, setNotificationMessage] = React.useState("");
    const [liveRefresh, setLiveRefresh] = React.useState(false);
    const [liveRefreshProgress, setLiveRefreshProgress] = React.useState(0);
    const [liveRefreshTimer, setLiveRefreshTimer] = React.useState<NodeJS.Timer | undefined>(undefined);
    const [nodes, setNodes] = React.useState<Node[]>([]);
    const [edges, setEdges] = React.useState<Edge[]>([]);

    const manager = React.useMemo(() => new ApiManager(), []);

    const getRecords = React.useCallback(async () => {
        const response = await manager.listRecords();
        setWebsiteRecords(response ?? []);
    }, [manager]);

    const notify = React.useCallback((severity: Severity, message: string) => {
        setNotificationMessage(message);
        setNotificationSeverity(severity);
        setNotificationOpen(true);
    }, [setNotificationOpen, setNotificationSeverity, setNotificationMessage]);

    const noFilter = -1;

    React.useEffect(() => {
        getRecords();
    }, [getRecords]);

    // this clears the timer on unmount
    React.useEffect(() => {
        return () => {
            if (liveRefreshTimer) {
                clearInterval(liveRefreshTimer);
            }
        };
    }, [liveRefreshTimer]);

    const handleWebsiteRecordFilter = (event: SelectChangeEvent<number | undefined>) => {
        const value = event.target.value;
        setWebsiteRecordFilter(value === undefined || value === noFilter ? undefined : Number(value));
    };

    const handleGraphViewChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setGraphView((event.target as HTMLInputElement).value);
    };

    const compareNodes = (oldNodes: Node[], newNodes: Node[]) => {
        if (oldNodes.length !== newNodes.length) {
            return false;
        }

        const dict: Record<string, Node> = {};
        oldNodes.forEach(node => dict[node.id] = node);

        return newNodes.every(node => {
            if (dict[node.id]) {
                const oldData = dict[node.id].data;
                const { data } = node;
                return oldData.crawlTime === data.crawlTime
                    && oldData.url === data.url
                    && oldData.owner === data.owner
                    && oldData.boundaryNode === data.boundaryNode;
            } else return false;
        })
    };

    const compareEdges = (oldEdges: Edge[], newEdges: Edge[]) => {
        if (oldEdges.length !== newEdges.length) {
            return false
        }

        const set = new Set<string>();
        oldEdges.forEach(edge => set.add(edge.id));

        return newEdges.every(edge => set.has(edge.id));
    }

    const getGraph = React.useCallback(async (records: number | undefined, graphView: string) => {
        setSelectedNode(null);
        if (records !== undefined) {
            const graph = await manager.getGraph(records.toString(), graphView);
            if (graph !== null) {
                const visualizer = new GraphVisualizer(graph);
                visualizer.layout();
                const visualizedGraph = visualizer.getGraph(800, 600);
                setNodes(oldNodes => {
                    let newNodes = oldNodes;
                    setEdges(oldEdges => {
                        if (!compareNodes(oldNodes, visualizedGraph.nodes) || !compareEdges(oldEdges, visualizedGraph.edges)) {
                            newNodes = visualizedGraph.nodes;
                            return visualizedGraph.edges;
                        }
                        return oldEdges;
                    });
                    return newNodes;
                });
                return;
            }
        }
        setNodes([]);
        setEdges([]);
    }, [setNodes, setEdges, manager]);

    React.useEffect(() => {
        getGraph(websiteRecordFilter, graphView);
    }, [getGraph, websiteRecordFilter, graphView]);

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

    const handleCloseEditModal = (editedRecord: number | null) => {
        setEditModalOpen(false);
        if (editedRecord !== null) {
            notify("success", "Record was successfully saved.");
            getRecords().then(() => {
                setWebsiteRecordFilter(editedRecord);
                setLiveRefresh(true);
            });
        }
    }

    const handleCreateWebsiteRecord = React.useCallback(() => {
        const newRecord = emptyWebsiteRecord();
        newRecord.url = selectedNode?.data.url;
        setEditedRecord(newRecord);
        setEditModalOpen(true);
    }, [setEditedRecord, setEditModalOpen, selectedNode]);

    const handleNotificationClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') {
            return;
        }
        setNotificationOpen(false);
    };

    const handleRecordExecuteClick = React.useCallback(async (id: number) => {
        const success = await manager.executeRecord(id);
        if (success) {
            notify("info", "Execution has started.");
            setLiveRefresh(true);
        } else {
            notify("error", "Failed to start the execution.");
        }
    }, [manager, notify]);

    const startProgress = React.useCallback(() => {
        setLiveRefreshProgress(0);
        const timer = setInterval(() => {
            setLiveRefreshProgress((prevProgress) => {
                if (prevProgress >= 100) {
                    // execute refresh
                    setLiveRefreshTimer((prevTimer) => {
                        if (prevTimer) {
                            clearInterval(prevTimer);
                        }
                        return undefined;
                    });
                    getGraph(websiteRecordFilter, graphView).then(startProgress);
                }
                return prevProgress >= 100 ? 100 : prevProgress + 10
            });
        }, 1000);
        setLiveRefreshTimer(timer);
    }, [setLiveRefreshTimer, setLiveRefreshProgress, getGraph, websiteRecordFilter, graphView]);

    const handleChangeLiveRefresh = (event: React.ChangeEvent<HTMLInputElement>) => {
        setLiveRefresh(event.target.checked);
    };

    React.useEffect(() => {
        if (liveRefresh) {
            // start timer
            startProgress();
        } else {
            // kill timer
            setLiveRefreshTimer((prevTimer) => {
                if (prevTimer) {
                    clearInterval(prevTimer);
                }
                return undefined;
            });
            setLiveRefreshProgress(0);
        }
    }, [liveRefresh, startProgress]);

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
                    {editModalOpen && <NewSiteModal handleClose={handleCloseEditModal} record={editedRecord} />}
                    <Toolbar
                        sx={{
                            pl: { sm: 2 },
                            pr: { xs: 1, sm: 1 },
                        }}
                    >
                        <Typography
                            sx={{ flex: '1 1 50%' }}
                            variant="h5"
                            id="tableTitle"
                            component="h1"
                            color="primary"
                        >
                            Visualisation
                        </Typography>
                        <FormControlLabel
                            value="start"
                            control={<Switch color="primary" checked={liveRefresh} onChange={handleChangeLiveRefresh} disabled={websiteRecordFilter === undefined} />}
                            label={(
                                <Stack direction={'row'} sx={{ alignItems: 'center' }}>
                                    <CircularProgress variant={liveRefreshProgress >= 100 ? "indeterminate" : "determinate"} value={liveRefreshProgress} sx={{ mr: 1 }} />
                                    <Typography>Live refresh</Typography>
                                </Stack>
                            )}
                            labelPlacement="start"
                            sx={{ minWidth: 200, mr: 3 }}
                        />
                        <FormControl sx={{ ml: 2, mr: 2 }}>
                            <FormLabel id="graph-view-radio-button">View mode</FormLabel>
                            <RadioGroup
                                row
                                name="graph-view-radio-button-group"
                                value={graphView}
                                onChange={handleGraphViewChange}
                                sx={{ minWidth: 300 }}
                            >
                                <FormControlLabel value="website" control={<Radio />} label="Website" />
                                <FormControlLabel value="domain" control={<Radio />} label="Domain" />
                            </RadioGroup>
                        </FormControl>
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
                    <Container maxWidth={false} sx={{ mt: 2, mb: 2, minWidth: 800, maxWidth: 1600, height: 614, padding: 0 }}>
                        <div style={{ display: 'flex', height: '100%' }}>
                            <div style={{ flex: '1 1 50%', border: '2px solid green', margin: 5 }}>
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
                            <div style={{ flexBasis: 'auto', width: 250, margin: 5 }}>
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
                                                    ? <Button variant="contained" onClick={() => handleRecordExecuteClick(selectedNode.data.owner)}>
                                                        Crawl {websiteRecords.filter(rec => rec.pk === websiteRecordFilter).map(rec => rec.label).join()} now
                                                    </Button>
                                                    : <Button variant="contained" onClick={handleCreateWebsiteRecord}>
                                                        Create new website record
                                                    </Button>}
                                            </React.Fragment>
                                        ) : (<Typography variant="body1">No selected item</Typography>)}
                                </Stack>
                            </div>
                        </div>
                    </Container>
                    <Snackbar
                        open={notificationOpen}
                        autoHideDuration={6000}
                        onClose={handleNotificationClose}
                        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
                    >
                        <Alert
                            onClose={handleNotificationClose}
                            severity={notificationSeverity}
                            sx={{ width: '100%' }}
                        >
                            {notificationMessage}
                        </Alert>
                    </Snackbar>
                </Container>
            </Box>
        </Box>
    );
}

export default function Visualisation() {
    return <VisualisationContent />;
}
