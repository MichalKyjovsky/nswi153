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
import Select, { SelectChangeEvent } from '@mui/material/Select';
import { ExecutionRecord } from './Common';
import ExecutionManager, { WebsiteRecordForSelect } from './ExecutionManager';

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
];

function ExecutionsContent() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(10);
    const [rows, setRows] = React.useState<ExecutionRecord[]>([]);
    const [totalRecords, setTotalRecords] = React.useState(0);
    const [websiteRecordFilter, setWebsiteRecordFilter] = React.useState<number | undefined>(undefined);
    const [websiteRecords, setWebsiteRecords] = React.useState<WebsiteRecordForSelect[]>([]);

    const manager = React.useMemo(() => new ExecutionManager(), []);

    const getRows = React.useCallback(async (pageSize: number, pageNumber: number, wrFilter?: number) => {
        const response = await manager.getPage(pageSize, pageNumber, wrFilter);
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
                                            <TableCell>{row.lastExecutionDuration}</TableCell>
                                            <TableCell>{row.sitesCrawled}</TableCell>
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
                </Container>
            </Box>
        </Box>
    );
}

export default function Executions() {
    return <ExecutionsContent />;
}
