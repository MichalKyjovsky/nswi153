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
import Chip from '@mui/material/Chip';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import SitesToolbar from './SitesToolbar';
import NewSiteModal from './EditSiteModal';
import { WebsiteRecord, emptyWebsiteRecord, createWebsiteRecord, WebsiteRecordForView, createWebsiteRecordForView, toPeriodicityString } from './Common';

type Order = 'asc' | 'desc';

interface HeadCell {
    disablePadding: boolean;
    id: keyof WebsiteRecordForView;
    label: string;
    align: "left" | "right" | "center";
    canFilter: boolean;
    canOrder: boolean;
    width?: number;
}

const headCells: readonly HeadCell[] = [
    {
        id: 'label',
        align: "left",
        disablePadding: false,
        label: 'Label',
        canFilter: true,
        canOrder: true,
    },
    {
        id: 'url',
        align: "left",
        disablePadding: false,
        label: 'URL',
        canFilter: true,
        canOrder: true,
    },
    {
        id: 'periodicity',
        align: "left",
        disablePadding: false,
        label: 'Periodicity',
        canFilter: false,
        canOrder: false,
        width: 130
    },
    {
        id: 'active',
        align: "left",
        disablePadding: false,
        label: 'Active',
        canFilter: false,
        canOrder: false,
        width: 75
    },
    {
        id: 'tags',
        align: "left",
        disablePadding: false,
        label: 'Tags',
        canFilter: true,
        canOrder: false,
    },
    {
        id: 'lastExecutionTime',
        align: "left",
        disablePadding: false,
        label: 'Last execution time',
        canFilter: false,
        canOrder: false,
        width: 175
    },
    {
        id: 'lastExecutionStatus',
        align: "left",
        disablePadding: false,
        label: 'Last execution status',
        canFilter: false,
        canOrder: false,
        width: 175
    },
    {
        id: 'actions',
        align: "left",
        disablePadding: false,
        label: 'Actions',
        canFilter: false,
        canOrder: false,
        width: 112
    },
];

interface SitesTableHeadProps {
    onRequestSort: (event: React.MouseEvent<unknown>, property: keyof WebsiteRecordForView) => void;
    order: Order;
    orderBy: string;
    filterListShown: boolean;
    onRequestFilter: (filterBy: keyof WebsiteRecordForView, filterPhrase: string) => void;
}

function SitesTableHead(props: SitesTableHeadProps) {
    const { order, orderBy, onRequestSort, filterListShown, onRequestFilter } = props;

    const [filters, setFilters] = React.useState<string[]>(Array.from({ length: headCells.length }).map(x => ""));
    const createSortHandler = (property: keyof WebsiteRecordForView) => (event: React.MouseEvent<unknown>) => {
        onRequestSort(event, property);
    };
    const createFilterHandler = (property: keyof WebsiteRecordForView, index: number) => (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter") {
            e.preventDefault();
            onRequestFilter(property, filters[index]);
        }
    }

    const createChangeHandler = (index: number) => (event: React.ChangeEvent<HTMLInputElement>) => {
        const newArray = filters.slice();
        newArray[index] = event.target.value;
        setFilters(newArray);
    };

    return (
        <TableHead>
            {filterListShown && (
                <TableRow>
                    {headCells.map((headCell, idx) => (
                        <TableCell key={`filter-${headCell.id}`}>
                            {headCell.canFilter && (<TextField label={headCell.label} onKeyPress={createFilterHandler(headCell.id, idx)} value={filters[idx]} onChange={createChangeHandler(idx)} variant="standard" />)}
                        </TableCell>))}
                </TableRow>)
            }
            <TableRow>
                {headCells.map((headCell) => (
                    <TableCell
                        key={headCell.id}
                        align={headCell.align}
                        padding={headCell.disablePadding ? 'none' : 'normal'}
                        sortDirection={orderBy === headCell.id ? order : false}
                        width={headCell.width}
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

interface ResponseRecordPage {
    model: string,
    pk: number,
    fields: {
        url: string,
        label: string,
        interval: number,
        active: boolean,
        regex: string
    },
    tags: string[],
    last_duration: number,
    last_status: string
}

interface ResponseData {
    records: ResponseRecordPage[],
    total_pages: number,
    total_records: number
}

interface ResponseRecord {
    model: string,
    pk: number,
    fields: {
        url: string,
        label: string,
        interval: number,
        status: number,
        regex: string,
        tags: string[]
    }
}

interface WebsiteResponse {
    records: WebsiteRecordForView[],
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

    async getPage(pageSize: number, pageNumber: number, labelFilter: string): Promise<WebsiteResponse | null> {
        try {
            const response = await this.inst.get(`record/${pageNumber + 1}/`, {
                params: {
                    page_size: pageSize,
                    "label-filter": labelFilter.trim().length > 0 ? labelFilter.trim() : undefined,
                }
            });
            const data: ResponseData = response.data;
            return {
                records: data.records.map(rec => createWebsiteRecordForView(rec.pk, rec.fields.url, rec.fields.label, toPeriodicityString(rec.fields.interval), rec.fields.active, rec.tags, rec.last_duration + "", rec.last_status)),
                totalPages: data.total_pages,
                totalRecords: data.total_records
            };
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async getRecord(id: number): Promise<WebsiteRecord | null> {
        try {
            const response = await this.inst.get("record/", {
                params: {
                    record: id
                }
            });
            const data: ResponseRecord[] = response.data;
            console.log("Get record data: ", data);
            const transformed = data.map(rec => createWebsiteRecord(rec.fields.url, rec.fields.label, rec.fields.interval, rec.fields.status === 1 ? true : false, rec.fields.regex, rec.fields.tags, rec.pk));
            console.log("Transformed data: ", transformed);
            return transformed.length > 0 ? transformed[0] : null;
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async deleteRecord(id: number) {
        const response = await this.inst.delete("record/", {
            data: {
                record_id: id
            }
        });
    }
}

function SitesContent() {
    const [page, setPage] = React.useState(0);
    const [rowsPerPage, setRowsPerPage] = React.useState(5);
    const [filterListShown, setFilterListShown] = React.useState(false);
    const [rows, setRows] = React.useState<WebsiteRecordForView[]>([]);
    const [totalRecords, setTotalRecords] = React.useState(0);
    const [editModalOpen, setEditModalOpen] = React.useState(false);
    const [editedRecord, setEditedRecord] = React.useState<WebsiteRecord>(emptyWebsiteRecord());
    const [confirmDeleteOpen, setConfirmDeleteOpen] = React.useState(false);
    const [deletedRecord, setDeletedRecord] = React.useState(0);
    const [labelFilter, setLabelFilter] = React.useState("");

    /** Enhanced table props */
    const [order, setOrder] = React.useState<Order>('asc');
    const [orderBy, setOrderBy] = React.useState<keyof WebsiteRecordForView>('label');

    const manager = React.useMemo(() => new WebsiteRecordManager(), []);
    const getRows = React.useCallback(async (pageSize: number, pageNumber: number, lblFilter: string) => {
        const response = await manager.getPage(pageSize, pageNumber, lblFilter);
        setRows(response ? response.records : []);
        response && setTotalRecords(response.totalRecords);
    }, [manager]);

    React.useEffect(() => {
        getRows(rowsPerPage, page, labelFilter);
    }, [page, rowsPerPage, labelFilter, getRows]);

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
        property: keyof WebsiteRecordForView,
    ) => {
        const isAsc = orderBy === property && order === 'asc';
        setOrder(isAsc ? 'desc' : 'asc');
        setOrderBy(property);
    };

    const handleRequestFilter = (
        property: keyof WebsiteRecordForView,
        value: string
    ) => {
        if (property === "label") {
            setLabelFilter(value);
        }
    };

    const handleCloseEditModal = (success: boolean) => {
        setEditModalOpen(false);
        if (success) {
            getRows(rowsPerPage, page, labelFilter);
        }
    }
    const handleAddRecordClick = () => {
        setEditedRecord(emptyWebsiteRecord());
        setEditModalOpen(true);
    }
    const handleEditRecordClick = async (id: number) => {
        const record = await manager.getRecord(id);
        if (record) {
            setEditedRecord(record);
            setEditModalOpen(true);
        }
    }

    const handleRecordDeleteClick = (id: number) => {
        setDeletedRecord(id);
        setConfirmDeleteOpen(true);
    };

    const handleRecordDeleteClose = async (shouldDelete: boolean) => {
        setConfirmDeleteOpen(false);
        if (shouldDelete) {
            try {
                await manager.deleteRecord(deletedRecord);
            } catch (error) {
                console.log(error);
            }
            getRows(rowsPerPage, page, labelFilter);
        }
    };
    /* Enhanced table props end */

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
                    <SitesToolbar toggleFilterList={setFilterListShown} addButtonClick={handleAddRecordClick} />
                    <TableContainer component={Paper} >
                        {editModalOpen && <NewSiteModal handleClose={handleCloseEditModal} record={editedRecord} />}
                        {confirmDeleteOpen && (
                            <Dialog
                                open={true}
                                onClose={() => handleRecordDeleteClose(false)}
                            >
                                <DialogTitle>{"Confirm delete"}</DialogTitle>
                                <DialogContent>
                                    <DialogContentText>
                                        Are you sure you want to delete this website record?
                                    </DialogContentText>
                                </DialogContent>
                                <DialogActions>
                                    <Button onClick={() => handleRecordDeleteClose(true)}>Delete</Button>
                                    <Button onClick={() => handleRecordDeleteClose(false)} autoFocus>
                                        Cancel
                                    </Button>
                                </DialogActions>
                            </Dialog>)
                        }
                        <Table sx={{ minWidth: 500 }} size={'small'}>
                            <SitesTableHead
                                order={order}
                                orderBy={orderBy}
                                onRequestSort={handleRequestSort}
                                onRequestFilter={handleRequestFilter}
                                filterListShown={filterListShown}
                            />
                            <TableBody>
                                {rows.map((row: WebsiteRecordForView, index: number) => {
                                    return (
                                        <TableRow
                                            hover
                                            tabIndex={-1}
                                            key={row.label}
                                        >
                                            <TableCell>{row.label}</TableCell>
                                            <TableCell>{row.url}</TableCell>
                                            <TableCell>{row.periodicity}</TableCell>
                                            <TableCell><Checkbox checked={row.active} /></TableCell>
                                            <TableCell>
                                                {
                                                    row.tags.map((tag: string, tagIndex: number) =>
                                                        <Chip
                                                            sx={{ ml: "1px", mr: "1px" }}
                                                            label={tag}
                                                            variant="outlined"
                                                            key={`itm-${index}-tag-${tagIndex}`}
                                                        />
                                                    )
                                                }
                                            </TableCell>
                                            <TableCell>{row.lastExecutionTime}</TableCell>
                                            <TableCell>{row.lastExecutionStatus}</TableCell>
                                            <TableCell>
                                                <IconButton onClick={() => handleEditRecordClick(row.pk)}><EditIcon /></IconButton>
                                                <IconButton onClick={() => handleRecordDeleteClick(row.pk)}><DeleteIcon /></IconButton>
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
                </Container>
            </Box>
        </Box>
    );
}

export default function Sites() {
    return <SitesContent />;
}
