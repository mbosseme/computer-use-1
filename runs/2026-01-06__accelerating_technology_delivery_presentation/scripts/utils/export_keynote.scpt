on run argv
    set pptxPath to item 1 of argv
    
    -- Keynote handles POSIX paths better usually
    set pptxFile to POSIX file pptxPath
    
    -- Target is ~/Pictures/AutoRender/output.pdf
    set pdfPath to (path to pictures folder as text) & "AutoRender:output.pdf"
    
    tell application "Keynote"
        activate
        try
            open pptxFile
        on error errMsg
             error "Keynote Failed to Open: " & errMsg
        end try
        
        set theDoc to the front document
        
        -- Export to PDF
        export theDoc to file pdfPath as PDF
        
        close theDoc saving no
    end tell
end run
