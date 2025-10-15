class WebSocketService {
    constructor() {this.socket = null, this.listeners = new Map();}

    connect(){
        const url = import.meta.env.VITE_WS_URL
        this.socket = new WebSocket(url);
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if(this.listeners.has(data.type)){
                this.listeners.get(data.type).forEach(cb => cb(data.payload))
            }
        }
    }

    send(type, payload){
        this.socket?.send(JSON.stringify({type, payload}))
    }

    subscribe(type, callback) {
        if(!this.listeners.has(type)) this.listeners.set(type, []);
        this.listeners.get(type).push(callback);
    }
}

export const wsService = new WebSocketService();