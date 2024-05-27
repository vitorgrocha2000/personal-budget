var dagcomponentfuncs = window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {};

dagcomponentfuncs.DeleteButton = function (props) {
    function onClick() {
        const { setData, cellRendererData } = props;
        setData(cellRendererData);  // Atualiza a propriedade cellRendererData
    }
    return React.createElement('button', { className: 'delete-statement-line-button', onClick }, "X");
};
