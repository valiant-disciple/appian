import { Sidebar } from "@/components/sidebar"
import { Editor } from "@/components/editor"

export default function Home() {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <main className="flex-1 flex">
        <Editor />
      </main>
    </div>
  )
} 