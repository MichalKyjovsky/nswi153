import * as React from 'react';
import Box from '@mui/material/Box';
import Container from '@mui/material/Container';
import Paper from '@mui/material/Paper';
import Table from '@mui/material/Table';
import TableHead from '@mui/material/TableHead';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableFooter from '@mui/material/TableFooter';
import TablePagination from '@mui/material/TablePagination';
import TableRow from '@mui/material/TableRow';
import TablePaginationActions from './TablePaginationActions';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import ExecutionIcon from '@mui/icons-material/Settings';
import IconButton from '@mui/material/IconButton';
import Tooltip from '@mui/material/Tooltip';
import Snackbar from '@mui/material/Snackbar';
import MuiAlert, { AlertProps } from '@mui/material/Alert';
import Select, { SelectChangeEvent } from '@mui/material/Select';
import { ExecutionRecord, toPeriodicityString } from './Common';
import ApiManager, { WebsiteRecordForSelect } from './ApiManager';

type Severity = "info" | "success" | "warning" | "error";

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
    props,
    ref,
) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

interface HeadCell {
    id: keyof ExecutionRecord;
    label: string;
    align: "left" | "right" | "center";
    width?: number;
}

const headCells: readonly HeadCell[] = [
    {
        id: 'websiteRecordLabel',
        align: "left",
        label: 'Website record',
    },
    {
        id: 'status',
        align: "left",
        label: 'Execution status',
    },
    {
        id: 'lastExecutionTime',
        align: "left",
        label: 'Last executed on',
    },
    {
        id: 'lastExecutionDuration',
        align: "left",
        label: 'Last execution duration',
    },
    {
        id: 'sitesCrawled',
        align: "left",
        label: 'Sites crawled',
    },
    {
        id: 'actions',
        align: "left",
        label: 'Actions',
        width: 80
    },
];

function ExecutionsContent() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [rows, setRows] = React.useState<ExecutionRecord[]>([]);
    const [totalRecords, setTotalRecords] = React.useState(0);
    const [websiteRecordFilter, setWebsiteRecordFilter] = React.useState<number | undefined>(undefined);
    const [websiteRecords, setWebsiteRecords] = React.useState<WebsiteRecordForSelect[]>([]);
    const [notificationOpen, setNotificationOpen] = React.useState(false);
    const [notificationSeverity, setNotificationSeverity] = React.useState<Severity>("info");
    const [notificationMessage, setNotificationMessage] = React.useState("");

    const manager = React.useMemo(() => new ApiManager(), []);

    const notify = React.useCallback((severity: Severity, message: string) => {
        setNotificationMessage(message);
        setNotificationSeverity(severity);
        setNotificationOpen(true);
    }, [setNotificationOpen, setNotificationSeverity, setNotificationMessage]);

    const getRows = React.useCallback(async (pageSize: number, pageNumber: number, wrFilter?: number) => {
        const response = await manager.getExecutionPage(pageSize, pageNumber, wrFilter);
        setRows(response ? response.executions : []);
        response && setTotalRecords(response.totalRecords);
    }, [manager]);

    const getRecords = React.useCallback(async () => {
        const response = await manager.listRecords();
        setWebsiteRecords(response ?? []);
    }, [manager]);

    const noFilter = -1;

    React.useEffect(() => {
        getRows(rowsPerPage, page, websiteRecordFilter);
    }, [page, rowsPerPage, websiteRecordFilter, getRows]);

    React.useEffect(() => {
        getRecords();
    }, [getRecords]);

    // Avoid a layout jump when reaching the last page with empty rows.
    const emptyRows = totalRecords > rowsPerPage ? rowsPerPage - rows.length : 0;

    const handleChangePage = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleWebsiteRecordFilter = (event: SelectChangeEvent<number | undefined>) => {
        const value = event.target.value;
        setWebsiteRecordFilter(value === undefined || value === noFilter ? undefined : Number(value));
        setPage(0);
    };

    const handleRecordExecuteClick = React.useCallback(async (id: number) => {
        const success = await manager.executeRecord(id);
        if (success) {
            notify("info", "Execution has started.");
        } else {
            notify("error", "Failed to start the execution.");
        }
    }, [manager, notify]);

    const handleNotificationClose = (event?: React.SyntheticEvent | Event, reason?: string) => {
        if (reason === 'clickaway') {
            return;
        }
        setNotificationOpen(false);
    };

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
                            Executions
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
                    <TableContainer component={Paper} >
                        <Table sx={{ minWidth: 500 }} size={'small'}>
                            <TableHead>
                                <TableRow>
                                    {headCells.map((headCell) => (
                                        <TableCell
                                            key={headCell.id}
                                            align={headCell.align}
                                            width={headCell.width}
                                        >
                                            {headCell.label}
                                        </TableCell>
                                    ))}
                                </TableRow>
                            </TableHead >
                            <TableBody>
                                {rows.map((row: ExecutionRecord, index: number) => {
                                    return (
                                        <TableRow
                                            hover
                                            tabIndex={-1}
                                            key={row.pk}
                                        >
                                            <TableCell>{row.websiteRecordLabel}</TableCell>
                                            <TableCell>{row.status}</TableCell>
                                            <TableCell>{row.lastExecutionTime}</TableCell>
                                            <TableCell>{toPeriodicityString(row.lastExecutionDuration)}</TableCell>
                                            <TableCell>{row.sitesCrawled}</TableCell>
                                            <TableCell>
                                                <Tooltip title="Execute">
                                                    <IconButton onClick={() => handleRecordExecuteClick(row.websiteRecordPk)}><ExecutionIcon /></IconButton>
                                                </Tooltip>
                                            </TableCell>
                                        </TableRow>
                                    );
                                })}
                                {emptyRows > 0 && (
                                    <TableRow
                                        style={{
                                            height: 55 * emptyRows,
                                        }}
                                    >
                                        <TableCell colSpan={6} />
                                    </TableRow>
                                )}
                            </TableBody>
                            <TableFooter>
                                <TableRow>
                                    <TablePagination
                                        rowsPerPageOptions={[5, 10, 25]}
                                        colSpan={6}
                                        count={totalRecords}
                                        rowsPerPage={rowsPerPage}
                                        page={page}
                                        onPageChange={handleChangePage}
                                        onRowsPerPageChange={handleChangeRowsPerPage}
                                        ActionsComponent={TablePaginationActions}
                                    />
                                </TableRow>
                            </TableFooter>
                        </Table>
                    </TableContainer>
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

export default function Executions() {
    return <ExecutionsContent />;
}
