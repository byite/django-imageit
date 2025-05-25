import Cropper from 'cropperjs';

type ImageitInputChangeCallback = (input: ImageitInput) => void;
type ImageProcessedCallback = (file: InputtedFile) => void;
type ToggleOptions = 'clear' | 'delete' | 'undo';

class ImageitInputHandler {
    private imageitInputs: ImageitInput[] = [];

    constructor(fileInputSelector: string, onFileChangeCallback: ImageitInputChangeCallback){
        let fileInputs = document.querySelectorAll<HTMLInputElement>(fileInputSelector);
        if (!fileInputs.length) {
            throw new Error(`No file input fields found with selector "${fileInputSelector}"`);
        }
        fileInputs.forEach((fileInput) => {
            let currentInput: ImageitInput | CropitInput; 
            if(fileInput.closest('.imageit-cropit-container')){
                currentInput = new CropitInput(fileInput, onFileChangeCallback);
            }else{
                currentInput = new ImageitInput(fileInput, onFileChangeCallback);
            }
            this.imageitInputs.push(currentInput);
        });
    }
}

class ImageitInput {
    fileInput: HTMLInputElement;
    container: Element;
    errors: string[] = [];
    initial: InitialFile;
    inputtedFiles: InputtedFile[] = [];
    multiFile: boolean = false;
    maxUploadSize: number;
    clearCheckbox: HTMLInputElement;
    allowedTypes: string[] = ['image/jpeg', 'image/png', 'application/pdf'];

    //Construct the class for each imageit input, raise a warning if no imageit form field found
    constructor(fileInputSelector: HTMLInputElement, onFileChangeCallback: ImageitInputChangeCallback){
        this.fileInput = fileInputSelector;
        this.container = this.fileInput.closest('.imageit-container');
        this.maxUploadSize = +this.fileInput.getAttribute('data-max_upload_size');
        this.clearCheckbox = this.container.querySelector('.imageit-clear-image-checkbox');

        if (!this.container) {
            console.warn('Imageit: No preview container found in', this.container);
            return;
        }
        this.retrieveInitial();
        this.initListeners(onFileChangeCallback);
        this.renderPreview();
    }

    //Add listeners to each imageit widget to listen for drag events, clicks. Changes to file inputs trigger ImageitInputChangeCallback
    initListeners(onFileChangeCallback: ImageitInputChangeCallback){
        // Drag and drop event listeners
        this.container.addEventListener('dragover', (e: DragEvent) => {
            e.preventDefault();
            this.container.classList.add('imageit-drag-active'); // Add styling class
        });

        this.container.addEventListener('dragleave', () => {
            this.container.classList.remove('imageit-drag-active'); // Remove styling class
        });

        this.container.addEventListener('drop', (e: DragEvent) => {
            e.preventDefault();
            this.container.classList.remove('imageit-drag-active'); // Remove styling class

            const files = e.dataTransfer?.files; // Access dataTransfer safely
            if (files) {
                this.fileInput.files = files; // Assign files to the input
                this.fileInput.dispatchEvent(new Event('change')); // Trigger change event
            }
        });

        // Allow click on container to trigger file input
        //this.container.addEventListener('click', () => this.fileInput.click());

        // Listen for changes in the file input
        this.fileInput.addEventListener('change', () => {
            this.errors = [];
            if (this.fileInput.files) {
                if(!this.multiFile && this.fileInput.files.length > 1){
                    this.errors.push("Multiple File Uploads Not Permitted. Select a Single File Only.");
                }else{
                    this.processInput();
                }
            }
            if (this.errors.length > 0){
                this.renderErrors();
                this.fileInput.value = "";
            }
            onFileChangeCallback(this);
        });
    }

    processInput(){
        Array.from(this.fileInput.files).forEach((file) => {
            let newFile = new InputtedFile(file);
            let dataValid = newFile.validateFile(this.maxUploadSize, this.allowedTypes);
            if (dataValid.result){
                if (this.multiFile){
                    this.inputtedFiles.push(newFile);
                }else{
                    this.inputtedFiles = [newFile];
                }
            }else{
                this.errors.push(...dataValid.data);
            }
        });
    }

    // Retrieve any initial files from the form
    private retrieveInitial(){
        this.container.querySelectorAll('.imageit-initial').forEach(item =>{
            //Instantiate image class for each of the initials
            let initialImg: HTMLImageElement = item.querySelector('.imageit-preview-image');

            this.initial = new InitialFile(initialImg.src);
        });
    }

    // Remove Initial file and check clear checkbox to prompt django to remove the image in the backend
    private toggleDeletion(){
        console.log(this);
        this.clearCheckbox.toggleAttribute("checked");
        console.log('marked for deletion');
        this.renderPreview();
    }

    // Remove any user inputted files
    private toggleClear(){
        console.log(`clear {this}`);
        this.inputtedFiles = [];
        this.fileInput.value = '';
        this.renderPreview();
    }

    // Render the Input Preview
    async renderPreview(): Promise<void> {
        return new Promise(async (resolve) => {
            let previewContainer = this.container.querySelector('.imageit-preview-container');
            this.container.classList.add('imageit-loading');
            if (!previewContainer) {
                console.warn('No preview container found.');
                return;
            }
            previewContainer.innerHTML = '';
            if (this.inputtedFiles.length > 0) {
                for (const file of this.inputtedFiles) {
                    const html = await file.generatePreviewHTML();
                    previewContainer.innerHTML += html;
                }
                previewContainer.appendChild(this.appendDiv('clear'));
                console.log('rendering inputted files');
            }else if(this.initial){
                if (!this.clearCheckbox.checked){
                    const html = await this.initial.generatePreviewHTML();
                    previewContainer.innerHTML += html;
                    previewContainer.appendChild(this.appendDiv('delete'));
                }else{
                    previewContainer.appendChild(this.appendDiv('undo'));
                };
                console.log('rendering initial');
            }else{
                console.log('No files to render.');
            }

            previewContainer.closest('.imageit-container').classList.remove('imageit-loading');

            this.container.dispatchEvent(new CustomEvent('imageit:rendered', {
                detail: { fileInputName: this.fileInput.name },
                bubbles: true
            }));

            resolve();
        });
    }

    renderErrors(){
        let previewContainer = this.container.querySelector('.imageit-preview-container');
        this.container.querySelectorAll('.imageit-error').forEach(elem => elem.remove());
        this.errors.forEach((error) => {
            let errorDiv = document.createElement("div");
            errorDiv.classList.add("imageit-error");
            errorDiv.textContent = error;
            previewContainer.appendChild(errorDiv);
        });
    }

    //Appeand a clear button to remove inputted files
    appendDiv(context: ToggleOptions){
        const newDiv = document.createElement('div');
        newDiv.classList.add('imageit-toggle', `imageit-${context}`);
        newDiv.textContent = context.charAt(0).toUpperCase() + context.slice(1);
        let func = this.toggleClear.bind(this);
        if (context == 'delete' || context == 'undo'){
            func = this.toggleDeletion.bind(this);
        }
        newDiv.addEventListener('click', event => { func()});
        return newDiv;
    }
}

class ImageitFile{
    file: File;
    descriptor: string;
    fileName: string;
    fileExtension: string;
    processedImage: string| ArrayBuffer;
    errors: string[] = [];
    clearable: boolean;
    removed: boolean = false;
    initial: boolean;

    //Construct the class for each file inputted
    constructor(file: File){
        this.file = file;
        this.fileName = file.name;
        this.fileExtension = this.fileName.split('.').pop().toLowerCase();
        this.clearable = true;
    }

    async getProcessedImage(): Promise<string|ArrayBuffer>{
        //Reads selected file and returns it
        //Returns Promise, resolves to img
        if (this.processedImage){
            return this.processedImage;
        }else{
            try {
                return new Promise((resolve) => {
                    if (!this.processedImage){
                        let reader = new FileReader();
                        reader.readAsDataURL(this.file);
                        reader.onloadend = (event) => {
                            this.processedImage = event.target?.result as string
                            resolve(this.processedImage);
                        };
                    }else{
                        resolve(this.processedImage);
                    }
                });   
            } catch (error) {
                this.errors.push(`Error processing file ${this.fileName}: ${error}`);
                console.error(`Error processing file ${this.fileName}:`, error);
            }
        }
    }

    async generatePreviewHTML(): Promise<string>{
        const processedFile = await this.getProcessedImage();
        let html = `
            <div class="imageit-preview">
                <div class="imageit-preview-content">
                    <a href="${processedFile}" target="_blank">
                        <img class="imageit-preview-image" alt="Image preview" src="${processedFile}" />
                    </a>
                    <div class="imageit-preview-text">
                        <p>
                            <strong class="imageit-preview-help-text">${this.descriptor}</strong>
                        </p>
                        <hr>
                        <p class="imageit-preview-filename">
                            ${this.fileName}
                        </p>
                    </div>
                </div>
            </div>
        `
        return html
    }
}

//Put "get processed image" into each child class, in the initial image one, read the url to a blob and then

class InitialFile extends ImageitFile{
    initial: boolean = true;

    //Construct the class for each initial file
    constructor(url: string){
        super(new File([], url.split('/').pop(), { type: url.split('.').pop().toLowerCase() }));
        this.descriptor = "Current";
        this.processedImage = url;
    }
}

class InputtedFile extends ImageitFile{
    initial: boolean = false;

    //Construct the class for each file inputted
    constructor(file: File){
        super(file);
        this.descriptor = "New";
        this.getProcessedImage();
    }

    //Validate the inputted file
    validateFile(maxUploadSize:number, allowedTypes: string[]): {result:boolean, data:string[]} {
        const maxFileSizeBytes = maxUploadSize * 1024 * 1024; // 5 MB

        if (!allowedTypes.includes(this.file.type)) {
            this.errors.push(`File type not allowed: ${this.file.type}`);
            return {result: false, data: this.errors};
        }
        if (this.file.size > maxFileSizeBytes) {
            this.errors.push(`File "${this.fileName}" exceeds ${maxUploadSize}MB limit: ${(this.file.size/1024/1024).toFixed(2)}MB`);
            return {result: false, data: this.errors};
        }
        return {result: true, data: ['']} // All files pass validation
    }
}

class InputtedCropFile extends InputtedFile{
    //Construct the class for each file inputted
    constructor(file: File){
        super(file);
    }

    async generatePreviewHTML(): Promise<string>{
        const processedFile = await this.getProcessedImage();
        console.log('Rendering Crop it image');
        let html = `
            <div class="imageit-preview">
                <div class="imageit-cropper-content">
                    <div class="imageit-cropper-image-container">
                    <img class="imageit-cropper-image" alt="Image crop preview" src="${processedFile}" />
                </div>
            </div>
        `
        return html
    }
}

class CropitInput extends ImageitInput{
    inputtedFiles: InputtedCropFile[] = [];
    cropValInputs: HTMLInputElement[] = [];
    cropVals: number[] = [];
    
    constructor(fileInputSelector: HTMLInputElement, onFileChangeCallback: ImageitInputChangeCallback){
        super(fileInputSelector, onFileChangeCallback);
        this.retrieveCropInputs();
    }

    initListeners(onFileChangeCallback: ImageitInputChangeCallback){
        // Listen for changes in the file input
        super.initListeners(onFileChangeCallback);
        this.container?.addEventListener('imageit:rendered', (e: CustomEvent) => {
            if(this.inputtedFiles.length >0){
                console.log('Preview completed in this container:', e.detail);
                let cropperElem = this.container.querySelector('.imageit-cropper-image') as HTMLImageElement;
                const cropper = new Cropper(cropperElem);
                cropperElem.addEventListener('crop', this.setCropVals.bind(this), false);
            }
        });
    }

    processInput(){
        Array.from(this.fileInput.files).forEach((file) => {
            let newFile = new InputtedCropFile(file);
            let dataValid = newFile.validateFile(this.maxUploadSize, this.allowedTypes);
            if (dataValid.result){
                if (this.multiFile){
                    this.inputtedFiles.push(newFile);
                }else{
                    this.inputtedFiles = [newFile];
                }
            }else{
                this.errors.push(...dataValid.data);
            }
        });
    }

    // Retrieve inputs for crop coordinates and add them to this.cropValInputs
    retrieveCropInputs(){
        let inputPrefix = this.fileInput.name.slice(0, -1);
        for(var i = 1; i <= 4; i++){
            console.log(this.container.querySelector('input[name="' + inputPrefix + i + '"]'));
            this.cropValInputs.push(this.container.querySelector('input[name="' + inputPrefix + i + '"]'));
        }
    }

    //Apply coordinates of crop to the relevant input fields
    setCropVals(e: CustomEvent<{ x: number; y: number; width: number; height: number }>){
        this.cropVals = [
            e.detail.x,
            e.detail.y,
            e.detail.x + e.detail.width,
            e.detail.y + e.detail.height
        ];

        for( var i=0; i < this.cropValInputs.length; i++){
            let inputField = this.cropValInputs[i];
            inputField.valueAsNumber = this.cropVals[i];
        }
    }
}

window.addEventListener("DOMContentLoaded", function(){
    // Instantiate the ImageitInputHandler
    new ImageitInputHandler('input[type="file"].imageit-file-selector', (input) => {
        input.renderPreview();
        if (input.fileInput.files) {
            console.log('Files:', Array.from(input.fileInput.files));
        } else {
            console.log('No files selected.');
        }
    });
});