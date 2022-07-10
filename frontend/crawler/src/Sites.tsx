import * as React from 'react';
import axios from 'axios';
import { AxiosInstance, AxiosResponse } from 'axios';
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
import Checkbox from '@mui/material/Checkbox';
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';
import FilterListIcon from '@mui/icons-material/FilterList';
import TextField from '@mui/material/TextField';
import SitesToolbar from './SitesToolbar';
import NewSiteModal from './EditSiteModal';
import { WebsiteRecord, emptyWebsiteRecord } from './Common';

interface Data {
    url: string;
    label: string;
    interval: number;
    status: boolean;
    regex: string;
}

function createData(
    url: string,
    label: string,
    interval: number,
    status: boolean,
    regex: string,
): Data {
    return {
        url,
        label,
        interval,
        status,
        regex,
    };
}

// let rows: Data[] = [];
// for (let i = 0; i < 20; i++) {
//     rows.push(createData('example.org', 'Example', 42, true, "./*"));
// }

function descendingComparator<T>(a: T, b: T, orderBy: keyof T) {
    if (b[orderBy] < a[orderBy]) {
        return -1;
    }
    if (b[orderBy] > a[orderBy]) {
        return 1;
    }
    return 0;
}

type Order = 'asc' | 'desc';

function getComparator<Key extends keyof any>(
    order: Order,
    orderBy: Key,
): (
        a: { [key in Key]: number | string | boolean },
        b: { [key in Key]: number | string | boolean },
    ) => number {
    return order === 'desc'
        ? (a, b) => descendingComparator(a, b, orderBy)
        : (a, b) => -descendingComparator(a, b, orderBy);
}

interface HeadCell {
    disablePadding: boolean;
    id: keyof Data;
    label: string;
    numeric: boolean;
    canFilter: boolean;
    canOrder: boolean;
}

const headCells: readonly HeadCell[] = [
    {
        id: 'label',
        numeric: false,
        disablePadding: true,
        label: 'Label',
        canFilter: true,
        canOrder: true,
    },
    {
        id: 'url',
        numeric: false,
        disablePadding: false,
        label: 'URL',
        canFilter: true,
        canOrder: true,
    },
    {
        id: 'interval',
        numeric: true,
        disablePadding: false,
        label: 'Periodicity',
        canFilter: false,
        canOrder: true,
    },
    {
        id: 'status',
        numeric: false,
        disablePadding: false,
        label: 'Active',
        canFilter: true,
        canOrder: true,
    },
    {
        id: 'regex',
        numeric: false,
        disablePadding: false,
        label: 'Regex',
        canFilter: false,
        canOrder: false,
    },
];

interface SitesTableHeadProps {
    numSelected: number;
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof Data) => void;
    onSelectAllClick: (event: React.ChangeEvent<HTMLInputElement>) => void;
    order: Order;
    orderBy: string;
    rowCount: number;
    filterListShown: boolean;
}

function SitesTableHead(props: SitesTableHeadProps) {
    const { onSelectAllClick, order, orderBy, numSelected, rowCount, onRequestSort, filterListShown } = props;
    const createSortHandler = (property: keyof Data) => (event: React.MouseEvent<unknown>) => {
        onRequestSort(event, property);
    };

    return (
        <TableHead>
            {filterListShown && (<TableRow>
                <TableCell align={'center'}><div style={{ verticalAlign: 'middle', display: 'inline-block', height: '24px' }}><FilterListIcon /></div></TableCell>
                {headCells.map((headCell) => (
                    <TableCell>
                        {headCell.canFilter && (<TextField label={headCell.label} variant="standard" />)}
                    </TableCell>))}
            </TableRow>)
            }
            <TableRow>
                <TableCell padding="checkbox">
                    <Checkbox
                        color="primary"
                        indeterminate={numSelected > 0 && numSelected < rowCount}
                        checked={rowCount > 0 && numSelected === rowCount}
                        onChange={onSelectAllClick}
                        inputProps={{
                            'aria-label': 'select all desserts',
                        }}
                    />
                </TableCell>
                {headCells.map((headCell) => (
                    <TableCell
                        key={headCell.id}
                        align={headCell.numeric ? 'right' : 'left'}
                        padding={headCell.disablePadding ? 'none' : 'normal'}
                        sortDirection={orderBy === headCell.id ? order : false}
                    >
                        {headCell.canOrder ? (
                            <TableSortLabel
                                active={orderBy === headCell.id}
                                direction={orderBy === headCell.id ? order : 'asc'}
                                onClick={createSortHandler(headCell.id)}
                            >
                                {headCell.label}
                                {orderBy === headCell.id ? (
                                    <Box component="span" sx={visuallyHidden}>
                                        {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                                    </Box>
                                ) : null}
                            </TableSortLabel>) : headCell.label}
                    </TableCell>
                ))}
            </TableRow>
        </TableHead >
    );
}

interface ResponseRecord {
    model: string,
    pk: number,
    fields: {
        url: string,
        label: string,
        interval: number,
        status: number,
        regex: string
    },
    tags: string[]
}

interface ResponseData {
    records: ResponseRecord[],
    total_pages: number,
    total_records: number
}

interface WebsiteResponse {
    records: Data[],
    totalPages: number,
    totalRecords: number
}

class WebsiteRecordManager {
    inst: AxiosInstance;

    constructor() {
        this.inst = axios.create({
            baseURL: 'http://localhost:8000/api/',
            timeout: 1000,
            //headers: {'X-Custom-Header': 'foobar'}
        });
    }

    async get(pageSize: number, pageNumber: number,): Promise<WebsiteResponse | null> {
        try {
            const response = await this.inst.get(`record/${pageNumber + 1}/`, {
                params: {
                    page_size: pageSize
                }
            });
            const data: ResponseData = response.data;
            return {
                records: data.records.map(rec => createData(rec.fields.url, rec.fields.label, rec.fields.interval, rec.fields.status === 1 ? true : false, rec.fields.regex)),
                totalPages: data.total_pages,
                totalRecords: data.total_records
            };
        } catch (error) {
            console.error(error);
        }
        return null;
    }
}

function SitesContent() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(5);
    const [filterListShown, setFilterListShown] = React.useState(false);
    const [rows, setRows] = React.useState<Data[]>([]);
    const [totalRecords, setTotalRecords] = React.useState(0);
    const [editModalOpen, setEditModalOpen] = React.useState(false);
    const [editedRecord, setEditedRecord] = React.useState<WebsiteRecord>(emptyWebsiteRecord());

    /** Enhanced table props */
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof Data>('label');
    const [selected, setSelected] = React.useState<readonly string[]>([]);

    const manager = new WebsiteRecordManager();
    const getRows = async (pageSize: number, pageNumber: number) => {
        const response = await manager.get(pageSize, pageNumber);
        setRows(response ? response.records : []);
        response && setTotalRecords(response.totalRecords);
    };

    React.useEffect(() => {
        getRows(rowsPerPage, page);
    }, [page, rowsPerPage]);

    // Avoid a layout jump when reaching the last page with empty rows.
    const emptyRows = totalRecords > rowsPerPage ? rowsPerPage - rows.length : 0;

    const handleChangePage = (event: React.MouseEvent<HTMLButtonElement> | null, newPage: number) => {
        setPage(newPage);
    };

    const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const handleRequestSort = (
        event: React.MouseEvent<unknown>,
        property: keyof Data,
    ) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.checked) {
            const newSelecteds = rows.map((n) => n.label);
            setSelected(newSelecteds);
            return;
        }
        setSelected([]);
    };

    const handleClick = (event: React.MouseEvent<unknown>, name: string) => {
        const selectedIndex = selected.indexOf(name);
        let newSelected: readonly string[] = [];

        if (selectedIndex === -1) {
            newSelected = newSelected.concat(selected, name);
        } else if (selectedIndex === 0) {
            newSelected = newSelected.concat(selected.slice(1));
        } else if (selectedIndex === selected.length - 1) {
            newSelected = newSelected.concat(selected.slice(0, -1));
        } else if (selectedIndex > 0) {
            newSelected = newSelected.concat(
                selected.slice(0, selectedIndex),
                selected.slice(selectedIndex + 1),
            );
        }

        setSelected(newSelected);
    };

    const handleCloseEditModal = () => setEditModalOpen(false);
    const handleAddRecordClick = () => {
        setEditedRecord(emptyWebsiteRecord());
        setEditModalOpen(true);
    }

    const isSelected = (name: string) => selected.indexOf(name) !== -1;
    /* Enhanced table props end */

    return (
        <Box sx={{ display: 'flex' }}>
            <Box
                component="main"
                sx={{
                    backgroundColor: (theme) => theme.palette.grey[100],
                    flexGrow: 1,
                    height: '100vh',
                    overflow: 'auto',
                }}
            >
                <Container maxWidth="lg" sx={{ mt: 2, mb: 2 }}>
                    <SitesToolbar numSelected={selected.length} toggleFilterList={setFilterListShown} addButtonClick={handleAddRecordClick} deleteButtonClick={() => { }} />
                    <TableContainer component={Paper} >
                        {editModalOpen && <NewSiteModal handleClose={handleCloseEditModal} record={editedRecord} />}
                        <Table sx={{ minWidth: 500 }} aria-label="custom pagination table" size={'small'}>
                            <SitesTableHead
                                numSelected={selected.length}
                                order={order}
                                orderBy={orderBy}
                                onSelectAllClick={handleSelectAllClick}
                                onRequestSort={handleRequestSort}
                                rowCount={rows.length}
                                filterListShown={filterListShown}
                            />
                            <TableBody>
                                {rows.map((row, index) => {
                                    const isItemSelected = isSelected(row.label);
                                    const labelId = `enhanced-table-checkbox-${index}`;

                                    return (
                                        <TableRow
                                            hover
                                            onClick={(event) => handleClick(event, row.label)}
                                            role="checkbox"
                                            aria-checked={isItemSelected}
                                            tabIndex={-1}
                                            key={row.label}
                                            selected={isItemSelected}
                                        >
                                            <TableCell padding="checkbox">
                                                <Checkbox
                                                    color="primary"
                                                    checked={isItemSelected}
                                                    inputProps={{
                                                        'aria-labelledby': labelId,
                                                    }}
                                                />
                                            </TableCell>
                                            <TableCell
                                                component="th"
                                                id={labelId}
                                                scope="row"
                                                padding="none"
                                            >
                                                {row.label}
                                            </TableCell>
                                            <TableCell>{row.url}</TableCell>
                                            <TableCell align="right">{row.interval}</TableCell>
                                            <TableCell ><Checkbox checked={row.status} /></TableCell>
                                            <TableCell >{row.regex}</TableCell>
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
                                        // SelectProps={{
                                        //     inputProps: {
                                        //         'aria-label': 'rows per page',
                                        //     },
                                        //     native: true,
                                        // }}
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

export default function Sites() {
    return <SitesContent />;
}
