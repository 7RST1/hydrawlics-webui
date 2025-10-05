import {SERVER_URL} from "./constants.ts";
import axios from "axios";

export type HConfig = {
    allowed_extensions: string[],
}

export const getConfig = async (): Promise<HConfig> => {
    const response = await axios.get(SERVER_URL + `/config`)
    return response.data as HConfig;
}