on run argv
    set pptxPath to item 1 of argv
    
    -- Convert POSIX to HFS Path manually if needed, or rely on POSIX file
    set pptxFile to (POSIX file pptxPath)
    
    -- FORCE PDF OUTPUT to ~/Pictures/AutoRender/output.pdf
    set pdfPath to (path to pictures folder as text) & "AutoRender:output.pdf"
    
    tell application "Microsoft PowerPoint"
        activate
        
        -- Try Opening
        try
            open pptxFile
        on error errMsg number errNum
            error "Failed to open " & pptxPath & ": " & errMsg number errNum
        end try
        
        set thePres to the active presentation
        
        -- DEBUG: Just wait a second
        delay 1
        
        -- EXPORT AS PDF (Explicit format)
        -- save thePres in pdfPath as save as PDF
        
        close thePres saving no
    end tell
end run
