import axios from 'axios';
import { AxiosInstance, AxiosResponse } from 'axios';

export interface Data {
    url: string;
    label: string;
    interval: number;
    status: boolean;
    regex: string;
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

export class WebsiteRecordManager {
    rows: (Data[] | null)[];
    pageSize: number;
    inst: AxiosInstance;

    constructor(pageSize: number) {
        this.rows = [];
        this.pageSize = pageSize;
        this.inst = axios.create({
            baseURL: 'http://localhost/api/',
            timeout: 1000,
            //headers: {'X-Custom-Header': 'foobar'}
        });
    }

    async get(pageNumber: number): Promise<Data[] | null> {
        if (this.rows.length > pageNumber && this.rows[pageNumber]) {
            // return cached data
            return this.rows[pageNumber];
        }
        try {
            const response = await this.inst.get(`record/${pageNumber}`, {
                params: {
                    page_size: this.pageSize
                }
            });
            while (this.rows.length < pageNumber) this.rows.push(null);
            const data: ResponseData = response.data;
            this.rows[pageNumber] = data.records.map(rec => createData(rec.fields.url, rec.fields.label, rec.fields.interval, rec.fields.status === 1 ? true : false, rec.fields.regex));
            return this.rows[pageNumber];
        } catch (error) {
            console.error(error);
        }
        return null;
    }
}