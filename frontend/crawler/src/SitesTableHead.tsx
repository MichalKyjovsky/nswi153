import * as React from 'react';
import Box from '@mui/material/Box';
import TableHead from '@mui/material/TableHead';
import TableCell from '@mui/material/TableCell';
import TableRow from '@mui/material/TableRow';
import TableSortLabel from '@mui/material/TableSortLabel';
import { visuallyHidden } from '@mui/utils';
import TextField from '@mui/material/TextField';
import { WebsiteRecordForView, Order } from './Common';

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
        id: 'last_crawl',
        align: "left",
        disablePadding: false,
        label: 'Last execution time',
        canFilter: false,
        canOrder: true,
        width: 185
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

export default function SitesTableHead(props: SitesTableHeadProps) {
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