# Tools 

Introduction to the concept of tools

## Tool making 

brief explanation of the code structure of a tool



<div style="border:1px solid #2d3748; border-radius:8px; overflow: visible; font-family:sans-serif;">
    <!-- Caixa principal -->
    <div style="border:1px solid #4a5568; padding:10px; border-radius:6px;">
    <div style="text-align:center; margin-bottom:10px; font-weight:bold;">Tool</div>
    <div style="display:flex; flex-direction: column; gap:10px;">
        <!-- requires -->
        <div style="
            border:1px solid #4a5568;
            padding:10px;
            border-radius:6px;
            white-space: nowrap;
            overflow-x: visible;
            ">
        class ToolNameSchema(BaseModel):<br>
        <p style="margin-top: 0; margin-bottom: 0; text-indent: 50px;"><i>parameter_1</i>: <i>type_1</i> = Field(..., description = "your  first param description")</p>
        <p style="margin-top: 0; margin-bottom: 0; text-indent: 50px;"><i>parameter_2</i>: <i>type_2</i> = Field(..., description = "your second param description")</p>
        <p style="margin-top: 0; margin-bottom: 0; text-indent: 50px;"><i>...</i></p><br>
        </div>
        <i>(The above block can be called as many times as required, if parameters correspond)</i>
        <!-- install -->
        <div style="
            border:1px solid #4a5568;
            padding:10px;
            border-radius:6px;
            white-space: nowrap;
            overflow-x: visible;
            ">
        @tool(args_schema = ToolNameSchema)<br>
        def toolname( <i>parameters</i> ):
            <i><p style="text-indent: 50px;">code.</p><i>
            <p style="margin-top: 0; margin-bottom: 0; text-indent: 50px;">return {"status": "succes", '__control__': 'done', 'any':'more data'}</p><br>
            <i>(You can add more items on return, or modify the "status" 
            variable to any other value).</i>
        <br><br>
        </div>
    </div>
    </div>
</div>