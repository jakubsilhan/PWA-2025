import { io } from 'socket.io-client'

class WebSocketService {
  socket = null

  connect() {
    // Creates a websocket service with specified connection details and connects to it
    const url = import.meta.env.VITE_WS_URL
    const wsPath =
      import.meta.env.VITE_WS_PATH !== undefined
        ? import.meta.env.VITE_WS_PATH
        : location.pathname.slice(0, location.pathname.lastIndexOf('/')) + '/api/socket.io'
    if (!this.socket) {
      this.socket = io(url, {
        withCredentials: true,
        // path:
        //   import.meta.env.VITE_WS_PATH ||
        //   location.pathname.slice(0, location.pathname.lastIndexOf('/')) + '/api/socket.io',
        path: wsPath,
        transports: ['websocket'],
      })

      // Adds logging callbacks for connect/disconnect
      this.socket.on('connect', () => console.log('WS connected:', this.socket.id))
      this.socket.on('disconnect', (reason) => console.log('WS disconnected:', reason))
    }
  }

  async disconnect() {
    // Disconnects from current websocket
    if (this.socket) {
      console.log('Disconnecting socket...')
      this.socket.disconnect()
      await new Promise((r) => setTimeout(r, 100))
      this.socket = null
    }
  }

  on(event, clb) {
    this.socket?.on(event, clb)
  }

  off(event, clb) {
    this.socket?.off(event, clb)
  }

  emit(event, data) {
    this.socket?.emit(event, data)
  }
}

// Creates a global websocket service
export const wsService = new WebSocketService()
