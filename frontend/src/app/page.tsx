"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { useForm } from "react-hook-form";
import { Scissors, Download, Video, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";


interface ClipFormValues {
  url: string;
  start: string;
  end: string;
}

interface VideoMetadata {
  title: string;
  thumbnail: string;
  duration_string: string;
  uploader: string;
}

export default function Home() {
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMessage, setProgressMessage] = useState("Processing your clip...");
  const [metadata, setMetadata] = useState<VideoMetadata | null>(null);
  const [isFetchingMetadata, setIsFetchingMetadata] = useState(false);

  const form = useForm<ClipFormValues>({
    defaultValues: {
      url: "",
      start: "00:00:00",
      end: "00:01:00",
    },
  });

  const watchUrl = form.watch("url");

  // Fetch metadata automatically when a valid YouTube URL is detected
  useEffect(() => {
    const fetchMetadata = async () => {
      const pattern = /^(https?\:\/\/)?(www\.youtube\.com|youtu\.be)\/.+$/;
      if (pattern.test(watchUrl)) {
        setIsFetchingMetadata(true);
        setMetadata(null); // Clear old metadata
        try {
          const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://youtubeclipperbackend.onrender.com";
          const response = await axios.post(`${apiUrl}/metadata`, { url: watchUrl });
          setMetadata(response.data);
        } catch (error) {
          console.error("Could not fetch metadata", error);
        } finally {
          setIsFetchingMetadata(false);
        }
      } else {
        setMetadata(null);
      }
    };

    const debounce = setTimeout(() => {
      if (watchUrl) fetchMetadata();
    }, 1000); // 1-second debounce to prevent spamming

    return () => clearTimeout(debounce);
  }, [watchUrl]);

  async function onSubmit(data: ClipFormValues) {
    let progressInterval: NodeJS.Timeout;
    try {
      setIsDownloading(true);
      setProgress(5); 
      setProgressMessage("Initializing download...");

      // Simulated background progress while backend works
      progressInterval = setInterval(() => {
        setProgress(p => {
          if (p < 25) {
            setProgressMessage("Extracting video from YouTube...");
            return p + 2;
          } else if (p < 60) {
             return p + 0.5;
          } else if (p < 90) {
             setProgressMessage("This is a large clip, still processing in the background...");
             return p + 0.1;
          } else if (p < 95) {
             setProgressMessage("Almost there, finalizing video file...");
             return p + 0.02;
          }
          return p;
        });
      }, 500);

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://youtubeclipperbackend.onrender.com";
      const response = await axios.post(`${apiUrl}/clip`, data, {
        responseType: "blob", 
        onDownloadProgress: (progressEvent) => {
          if (progressEvent.total) {
            clearInterval(progressInterval);
            setProgressMessage("Downloading to browser...");
            const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setProgress(95 + (percentCompleted * 0.05));
          }
        },
      });

      clearInterval(progressInterval);
      setProgress(100);
      setProgressMessage("Done!");

      // Trigger browser file download
      const filename = metadata ? `${metadata.title.replace(/[^a-z0-9]/gi, '_').toLowerCase()}_clip.mp4` : "youtube_clip.mp4";
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);
      
    } catch (error: any) {
      clearInterval(progressInterval!);
      console.error("Failed to download clip", error);
      let errorMsg = "Failed to process the clip. Please check the URL and timestamps.";
      if (error.response && error.response.data) {
        // Read blob as text to get error message
        try {
            const text = await error.response.data.text();
            const json = JSON.parse(text);
            if (json.detail) {
                errorMsg = json.detail;
            }
        } catch (e) {
            console.error("Failed to parse error response", e);
        }
      }
      alert(errorMsg);
    } finally {
      setIsDownloading(false);
      setProgress(0);
      setProgressMessage("Processing your clip...");
    }
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900 flex flex-col items-center justify-center p-4 md:p-8 relative overflow-hidden">
      {/* Soft, friendly background blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[50vw] h-[50vw] bg-blue-400/20 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50vw] h-[50vw] bg-purple-400/20 rounded-full blur-[100px] pointer-events-none" />
      
      <div className="w-full max-w-lg space-y-8 z-10 animate-in fade-in slide-in-from-bottom-4 duration-700">
        <div className="text-center space-y-3">
          <div className="inline-flex items-center justify-center p-4 bg-white rounded-3xl shadow-sm border border-slate-100 mb-2 hover:scale-105 transition-transform">
            <Scissors className="w-10 h-10 text-blue-600" />
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight text-slate-900">
            YouTube Clipper
          </h1>
          <p className="text-slate-500 text-lg md:text-xl max-w-sm mx-auto">
            The easiest way to grab a specific moment from any video.
          </p>
        </div>

        <Card className="border-0 shadow-2xl shadow-slate-200/80 bg-white/90 backdrop-blur-2xl rounded-[2rem] overflow-hidden">
          <CardContent className="p-6 md:p-8">
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                
                {/* URL Input */}
                <div className="space-y-2">
                  <label className="text-slate-700 font-semibold text-base">Video Link</label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <Video className="h-6 w-6 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
                    </div>
                    <Input 
                      placeholder="https://youtube.com/watch?v=..." 
                      className="pl-12 h-14 text-lg bg-slate-50 border-slate-200 focus-visible:ring-blue-500 focus-visible:border-blue-500 rounded-2xl transition-all shadow-sm" 
                      {...form.register("url")} 
                    />
                  </div>
                </div>

                {/* Metadata Preview */}
                {isFetchingMetadata && (
                  <div className="flex items-center justify-center gap-3 text-slate-500 p-4 bg-slate-50 rounded-2xl animate-pulse">
                    <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                    <span className="font-medium">Finding video...</span>
                  </div>
                )}
                
                {metadata && (
                  <div className="flex gap-4 p-4 bg-white border border-slate-100 rounded-2xl shadow-sm animate-in fade-in zoom-in duration-300 hover:shadow-md transition-shadow">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img src={metadata.thumbnail} alt={metadata.title} className="w-28 h-20 object-cover rounded-xl shadow-sm" />
                    <div className="flex flex-col justify-center overflow-hidden">
                      <p className="text-base font-bold text-slate-800 truncate" title={metadata.title}>
                        {metadata.title}
                      </p>
                      <p className="text-sm text-slate-500">{metadata.uploader}</p>
                      <div className="mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 w-fit">
                        {metadata.duration_string}
                      </div>
                    </div>
                  </div>
                )}

                {/* Timestamps */}
                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="space-y-2">
                    <label className="text-slate-700 font-semibold text-base">Start Time</label>
                    <Input 
                      placeholder="00:00:00" 
                      className="h-14 text-center text-lg font-mono bg-slate-50 border-slate-200 focus-visible:ring-blue-500 rounded-2xl shadow-sm" 
                      {...form.register("start")} 
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-slate-700 font-semibold text-base">End Time</label>
                    <Input 
                      placeholder="00:01:00" 
                      className="h-14 text-center text-lg font-mono bg-slate-50 border-slate-200 focus-visible:ring-blue-500 rounded-2xl shadow-sm" 
                      {...form.register("end")} 
                    />
                  </div>
                </div>

                {/* Progress Bar */}
                {isDownloading && (
                  <div className="space-y-3 pt-4 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex justify-between text-sm font-medium text-slate-600">
                      <span>{progressMessage}</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="h-3 bg-slate-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-blue-500 transition-all duration-300 ease-out"
                        style={{ width: `${progress}%` }}
                      />
                    </Progress>
                  </div>
                )}

                {/* Submit Button */}
                <Button 
                  type="submit" 
                  className="w-full h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-2xl transition-all font-bold text-lg mt-8 shadow-lg shadow-blue-600/20 active:scale-[0.98]"
                  disabled={isDownloading || isFetchingMetadata || (!metadata && form.getValues('url') !== '')}
                >
                  {isDownloading ? (
                    <span className="flex items-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      Downloading...
                    </span>
                  ) : (
                    <span className="flex items-center gap-2">
                      <Download className="w-5 h-5" />
                      {metadata ? "Download Clip" : "Waiting for URL..."}
                    </span>
                  )}
                </Button>
              </form>
          </CardContent>
        </Card>
      </div>
    </main>
  );
}
