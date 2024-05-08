<!-- Improved compatibility of back to top link: See: https://github.com/BSolarV/OracleDBAuditor/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Oracle DataBase Auditor</h3>

  <p align="center">
    Script to automate Oracle Database Server security audit. <br>
	For Oracle Database Server 10G, 11G, 12C and 19C .
    <br />
    <a href="https://github.com/BSolarV/OracleDBAuditor"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/BSolarV/OracleDBAuditor/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/BSolarV/OracleDBAuditor/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

<!-- ( [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

Our project aims to streamline the often complex and time-consuming process of ensuring the security and integrity of your Oracle databases. Oracle DataBase Auditor scan your database, identify potential vulnerabilities, and generate comprehensive reports, allowing you to proactively address security risks and maintain compliance with industry standards.

This tool is based on the [Oracle](https://github.com/Jean-Francois-C/Database-Security-Audit/blob/master/ORACLE%20database%20penetration%20testing) checklist list at [Database-Security-Audit](https://github.com/Jean-Francois-C/Database-Security-Audit/tree/master) by [Jean-Francois](https://github.com/Jean-Francois-C).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

* [![Python][Python]][Python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1. Python > 3.7

2. SQL\*Plus  
SQL\*Plus must be installed in the system and in the PATH.

3. User with privileges on Oracle Database Server.  
Minimum privileges required:
	```
	SELECT_CATALOG_ROLE
	SELECT ANY DICTIONARY
	```

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/BSolarV/OracleDBAuditor.git
   ```
3. Install python requirements
   ```sh
   pip install -r requirements.txt
   ```
4. Set-up `.env` file
   ```
	USERNAME=<your oracle user>
	PASS=<oracle user pass>
	HOST=<host with oracle db service>
	PORT=<port service is running on>
	SID=<SID of oracle db>
   ```
   Ex: 
   ```
	USERNAME=USER01
	PASS=PASSWORD1
	HOST=localhost
	PORT=1521
	SID=ORACLE
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Information gathering
With the `.env` file in the folder, run the script to gather the information and execute the python script.
```
Usage: ./run.sh -dbv DATABASE_VERSION [-p] [-e ENV_FILE] [-h]  
Options:  
	-dbv, --database-version    Specify Oracle DB version (10g, 11g, 12c, 19c).  
	-p, --password-hashes       Retrieve password hashes of users.  
	-e, --env-file              Specify the .env file (default is .env)  
	-h, --help                  Display this help message.  
```
Ex:
```
./run.sh -dbv 10g -p
```

### Just information audit
After the information is gathered, the python script can be executed by it's own.
```
Usage: oracle_auditor.py [-h] -dbv DATABASE_VERSION -f FOLDER_PATH [-o OUT_FOLDER_PATH] [--active-users-audit] [-v, -vv, -vvv]
Options:
  -h, --help            show this help message and exit
  -dbv DATABASE_VERSION, --database-version DATABASE_VERSION
                        Specify Oracle DB version (10g, 11g, 12c, 19c).
  -f FOLDER_PATH, --folder-path FOLDER_PATH
                        Path to the folder containing .txt files
  -o OUT_FOLDER_PATH, --out-folder-path OUT_FOLDER_PATH
                        Path to the folder containing .txt files
  --active-users-audit  Path to the folder containing .txt files
  -v, --verbose         Verbosity Level. (-v to -vvv)
```
Ex:
```
python oracle_auditor.py -f .\Report-ORACLE -dbv 10g --active-users-audit
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [ ] Add verbosity to python scripts.
- [ ] Add audit to database querys permissions and audit configuration.

See the [open issues](https://github.com/BSolarV/OracleDBAuditor/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

Your Name - [@BSolarV](https://github.com/BSolarV) - bastian.solar.v@gmail.com

Project Link: [https://github.com/BSolarV/OracleDBAuditor](https://github.com/your_username/repo_name)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/BSolarV/OracleDBAuditor.svg?style=for-the-badge
[contributors-url]: https://github.com/BSolarV/OracleDBAuditor/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/BSolarV/OracleDBAuditor.svg?style=for-the-badge
[forks-url]: https://github.com/BSolarV/OracleDBAuditor/network/members
[stars-shield]: https://img.shields.io/github/stars/BSolarV/OracleDBAuditor.svg?style=for-the-badge
[stars-url]: https://github.com/BSolarV/OracleDBAuditor/stargazers
[issues-shield]: https://img.shields.io/github/issues/BSolarV/OracleDBAuditor.svg?style=for-the-badge
[issues-url]: https://github.com/BSolarV/OracleDBAuditor/issues
[license-shield]: https://img.shields.io/github/license/BSolarV/OracleDBAuditor.svg?style=for-the-badge
[license-url]: https://github.com/BSolarV/OracleDBAuditor/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/bsolarv

[product-screenshot]: images/screenshot.png

[Python]: https://img.shields.io/badge/Python-000000?style=for-the-badge&logo=python&logoColor=yellow
[Python-url]: https://python.org/
