"""
LilyPond Preview Tool - FastAPI Backend
金管編曲プレビュー・変換ツール
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import tempfile
import os
import shutil
from pathlib import Path
import base64

app = FastAPI(
    title="LilyPond Preview Tool",
    description="金管編曲のためのLilyPondプレビュー・変換ツール",
    version="1.0.0"
)

# CORS設定（開発用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LilyPondCode(BaseModel):
    code: str
    format: str = "pdf"  # pdf, midi, svg

class RenderResponse(BaseModel):
    success: bool
    pdf: str = None  # base64
    mp3: str = None  # base64（MIDIからMP3に変更）
    svg: str = None
    error: str = None

@app.get("/")
async def root():
    """フロントエンドを表示"""
    return FileResponse("index.html")

@app.get("/health")
async def health():
    """ヘルスチェック"""
    # LilyPondがインストールされているか確認
    try:
        result = subprocess.run(
            ["lilypond", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        lilypond_available = result.returncode == 0
        version = result.stdout.split('\n')[0] if lilypond_available else None
    except:
        lilypond_available = False
        version = None
    
    return {
        "status": "healthy",
        "lilypond_available": lilypond_available,
        "lilypond_version": version
    }

@app.post("/render", response_model=RenderResponse)
async def render_lilypond(request: LilyPondCode):
    """
    LilyPondコードをレンダリング（PDF優先）
    """
    # 一時ディレクトリを作成
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        ly_file = tmppath / "input.ly"
        
        # LilyPondコードをファイルに書き込み
        ly_file.write_text(request.code, encoding='utf-8')
        
        try:
            # LilyPondを実行（PDF + MIDI生成）
            result = subprocess.run(
                [
                    "lilypond",
                    "--pdf",
                    "--png",
                    "-dmidi-extension=midi",
                    "-dbackend=eps",
                    f"-o{tmppath / 'output'}",
                    str(ly_file)
                ],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return RenderResponse(
                    success=False,
                    error=f"LilyPond error: {result.stderr}"
                )
            
            # 出力ファイルを読み込み
            response = RenderResponse(success=True)
            
            # PDF（優先）
            pdf_file = tmppath / "output.pdf"
            if pdf_file.exists():
                with open(pdf_file, "rb") as f:
                    response.pdf = base64.b64encode(f.read()).decode('utf-8')
            
            # MIDI → MP3変換（時間がかかる処理）
            midi_file = tmppath / "output.midi"
            if midi_file.exists():
                try:
                    # FluidSynthでMIDI → WAV変換
                    wav_file = tmppath / "output.wav"
                    fluidsynth_result = subprocess.run(
                        [
                            "fluidsynth",
                            "-ni",
                            "/usr/share/sounds/sf2/FluidR3_GM.sf2",
                            str(midi_file),
                            "-F", str(wav_file),
                            "-r", "44100"
                        ],
                        capture_output=True,
                        timeout=30
                    )
                    
                    # FFmpegでWAV → MP3変換
                    if wav_file.exists() and fluidsynth_result.returncode == 0:
                        mp3_file = tmppath / "output.mp3"
                        ffmpeg_result = subprocess.run(
                            [
                                "ffmpeg",
                                "-i", str(wav_file),
                                "-acodec", "libmp3lame",
                                "-ab", "128k",
                                str(mp3_file),
                                "-y"  # 上書き
                            ],
                            capture_output=True,
                            timeout=30
                        )
                        
                        if mp3_file.exists() and ffmpeg_result.returncode == 0:
                            with open(mp3_file, "rb") as f:
                                response.mp3 = base64.b64encode(f.read()).decode('utf-8')
                except Exception as e:
                    # MP3変換失敗時はログのみ（PDF表示は継続）
                    print(f"MP3 conversion error: {e}")
            
            # SVG（PNGから生成される場合もある）
            svg_file = tmppath / "output.svg"
            if svg_file.exists():
                response.svg = svg_file.read_text(encoding='utf-8')
            
            return response
            
        except subprocess.TimeoutExpired:
            return RenderResponse(
                success=False,
                error="LilyPond processing timeout (30s)"
            )
        except Exception as e:
            return RenderResponse(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

@app.post("/convert/xml2ly")
async def convert_musicxml_to_lilypond(file: UploadFile = File(...)):
    """
    MusicXMLをLilyPondに変換
    """
    if not file.filename.endswith(('.xml', '.musicxml', '.mxl')):
        raise HTTPException(400, "File must be MusicXML (.xml, .musicxml, or .mxl)")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # アップロードされたファイルを保存
        xml_file = tmppath / file.filename
        with open(xml_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        try:
            # musicxml2lyを実行
            output_file = tmppath / "output.ly"
            result = subprocess.run(
                [
                    "musicxml2ly",
                    "-o", str(output_file),
                    str(xml_file)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return JSONResponse(
                    status_code=400,
                    content={
                        "success": False,
                        "error": f"musicxml2ly error: {result.stderr}"
                    }
                )
            
            # LilyPondコードを読み込み
            lilypond_code = output_file.read_text(encoding='utf-8')
            
            return {
                "success": True,
                "lilypond_code": lilypond_code,
                "message": "MusicXML converted to LilyPond successfully"
            }
            
        except subprocess.TimeoutExpired:
            return JSONResponse(
                status_code=408,
                content={
                    "success": False,
                    "error": "Conversion timeout (30s)"
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": f"Unexpected error: {str(e)}"
                }
            )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
