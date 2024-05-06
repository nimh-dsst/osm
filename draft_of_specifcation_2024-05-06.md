
# Initial Software Specification for OpenSciMetrics (OSM)

## 1. Overview
The OpenSciMetrics (OSM) application is a command-line tool designed for the evaluation of bibliometric indicators related to transparency, data sharing, rigor, and open science in biomedical publications. The application processes a PDF of a scientific publication, extracts relevant data, and outputs a JSON file with an array of bibliometric indicators.

## 2. Functional Requirements

### 2.1 Input
- **PDF File**: A PDF document of a biomedical publication.
- **Unique Identifier**: This can be a DOI (Digital Object Identifier), a PubMed ID, or an OpenAlex ID.

### 2.2 Processing
- **PDF to XML Conversion**: The application will utilize ScienceBeam Parser to convert the PDF document into an XML format.
- **Indicator Extraction**: Using the [rtransparent](https://github.com/serghiou/rtransparent) tool, the application will analyze the XML to extract and generate a set of indicators and metrics regarding the publication's adherence to open science principles.

### 2.3 Output
- **JSON File**: The output will be a JSON file containing:
  - An array of bibliometric indicators and metrics.
  - Additional metadata including:
    - Version of the OSM application.
    - Unique identifier for the Docker container.
    - MD5 hashes of the original PDF and the generated XML file.

## 3. System Architecture

The architecture will largely mimic an existing application our group has been involved in called `MRIQC` ([Code](https://github.com/nipreps/mriqc/) and [Documentation](https://mriqc.readthedocs.io/en/latest/) are publicly available.)

### 3.1 Containerization
- **Docker**: The application will be containerized using Docker, ensuring consistency across different computing environments and facilitating easy distribution and deployment.

### 3.3 External Dependencies
- **ScienceBeam Parser**: Available at https://github.com/elifesciences/sciencebeam-parser
- **rtransparent Tool**: A tool that will be integrated into the application workflow for analyzing XML data.
- **oddpub**: https://github.com/quest-bih/oddpub
- **R**

## 4. Development Environment

### 4.1 Source Code Management
- **GitHub Repository**: The application's source code and documentation will be maintained in the GitHub repository at https://github.com/nimh-dsst/OpenSciMetrics.

### 4.2 Programming languages
- Although some of the tools used in OSM are written in R, it will be written entirely in Python


### 4.3 Documentation
- The app will be documented using readthedocs, similar to [MRIQC](https://mriqc.readthedocs.io/en/latest/).

## 5. Version Control
- **Semantic Versioning**: The application will adhere to semantic versioning to manage versions of the software effectively.

## 6. Testing and Quality Assurance
- **Unit Tests**: Will cover individual components and functions.
- **Integration Tests**: To ensure that the components work together as expected.
- **Continuous Integration**: Automated tests will run for every commit and pull request using GitHub Actions.

## 7. Deployment
- **Docker Hub**: The Docker image will be available on Docker Hub for easy retrieval and deployment.
- **Automated Build**: Automated Docker builds will be set up to ensure that the latest version is always available for deployment.

## 8. Usage
The application will be run from the command line within the Docker container, taking the following arguments:
```bash
docker run -v /path/to/pdf:/data osm-image <PDF file path> <Unique Identifier>
```

This specification outlines the requirements and design for the OpenSciMetrics application, setting the groundwork for development, deployment, and usage in assessing open science practices in biomedical research.
