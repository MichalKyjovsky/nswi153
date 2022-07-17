import axios from 'axios';
import { AxiosInstance } from 'axios';
import { ExecutionRecord, createExecutionRecord, API_BASE_URL } from './Common';

interface ResponseExecutionPage {
    model: string,
    pk: number,
    fields: {
        title: string,
        url: string,
        crawl_duration: number,
        last_crawl: string,
        website_record: number,
        status: string,
        label: string
    },
    links: number
}

interface ResponseData {
    executions: ResponseExecutionPage[],
    total_pages: number,
    total_records: number
}

interface ExecutionsResponse {
    executions: ExecutionRecord[],
    totalPages: number,
    totalRecords: number
}

interface RecordsListResponse {
    records: WebsiteRecordForSelect[]
}

export interface WebsiteRecordForSelect {
    pk: number,
    label: string
}

export default class ExecutionManager {
    inst: AxiosInstance;

    constructor() {
        this.inst = axios.create({
            baseURL: API_BASE_URL,
            timeout: 1000,
        });
    }

    async getPage(pageSize: number, pageNumber: number, websiteFilter?: number): Promise<ExecutionsResponse | null> {
        try {
            const path = `execution${websiteFilter ? `/${websiteFilter}/` : "s/"}${pageNumber + 1}/`;
            const response = await this.inst.get(path, {
                params: {
                    page_size: pageSize
                }
            });
            const data: ResponseData = response.data;
            return {
                executions: data.executions.map(rec => createExecutionRecord(rec.pk, rec.fields.label, rec.fields.website_record, rec.fields.status, rec.fields.last_crawl, rec.fields.crawl_duration, rec.links)),
                totalPages: data.total_pages,
                totalRecords: data.total_records
            };
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async listRecords(): Promise<WebsiteRecordForSelect[] | null> {
        try {
            const path = 'record/list/';
            const response = await this.inst.get(path);
            const data: RecordsListResponse = response.data;
            return data.records;
        } catch (error) {
            console.error(error);
        }
        return null;
    }
}