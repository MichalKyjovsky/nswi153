import axios from 'axios';
import { AxiosInstance } from 'axios';
import {
    WebsiteRecordForView,
    createWebsiteRecordForView,
    toPeriodicityString,
    WebsiteRecord,
    createWebsiteRecord,
    API_BASE_URL,
    Order
} from './Common';

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
    last_crawl: string,
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

export default class WebsiteRecordManager {
    inst: AxiosInstance;

    constructor() {
        this.inst = axios.create({
            baseURL: API_BASE_URL,
            timeout: 1000,
        });
    }

    async getPage(pageSize: number, pageNumber: number, labelFilter: string, tagsFilter: string, urlFilter: string, order: Order, orderBy: keyof WebsiteRecordForView): Promise<WebsiteResponse | null> {
        try {
            const response = await this.inst.get(`record/${pageNumber + 1}/`, {
                params: {
                    page_size: pageSize,
                    "label-filter": labelFilter.trim().length > 0 ? labelFilter.trim() : undefined,
                    "url-filter": urlFilter.trim().length > 0 ? urlFilter.trim() : undefined,
                    "tag-filter": tagsFilter.trim().length > 0 ? tagsFilter.trim() : undefined,
                    sort_property: orderBy,
                    sort_order: order.toUpperCase()
                }
            });
            const data: ResponseData = response.data;
            return {
                records: data.records.map(rec => createWebsiteRecordForView(rec.pk, rec.fields.url, rec.fields.label, toPeriodicityString(rec.fields.interval), rec.fields.active, rec.tags, rec.last_crawl, rec.last_status)),
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
            const transformed = data.map(rec => createWebsiteRecord(rec.fields.url, rec.fields.label, rec.fields.interval, rec.fields.status === 1 ? true : false, rec.fields.regex, rec.fields.tags, rec.pk));
            return transformed.length > 0 ? transformed[0] : null;
        } catch (error) {
            console.error(error);
        }
        return null;
    }

    async deleteRecord(id: number) {
        await this.inst.delete("record/", {
            data: {
                record_id: id
            }
        });
    }
}