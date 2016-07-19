Webcrawler is implemented through Selenium Webdriver and safari driver libraries
It looks for the domain. It will find the resources deployed inside the application server container for the domain we entered
It will find for anchor <a> tag href element to find the list of hyper links inside the web resources.
output is as below
xpath .//*[@id='menu-main']/li[1]/ul[1]/li[1]/a[@href='http://wiprodigital.com/#section-our-story']
xpath .//*[@id='menu-main']/li[2]/a[@href='http://wiprodigital.com/#section-the-is']
xpath .//*[@id='menu-main']/li[3]/a[@href='http://wiprodigital.com/#section-agile']
xpath .//*[@id='menu-main']/li[4]/a[@href='http://wiprodigital.com/#section-our-evangelists']
xpath .//*[@id='menu-main']/li[5]/a[@href='http://wiprodigital.com/#section-our-tweets']
xpath .//*[@id='menu-main']/li[6]/a[@href='http://wiprodigital.com/#section-from-our-blog']

Prequisite for running this application.

os.name: 'Mac OS X' 
os.arch: 'x86_64'
 os.version: '10.11.5'
java.version: '1.8.0_71'
Safari Version : 'Version 9.1.1 (11601.6.17)'
Safari Driver : SafariDriver.safariextz.zip (double click on this ,  it will install on safari)
IDE :  Spring Tool suite(STS)
Libraries 
apache-mime4j-0.6.jar bsh-2.0b4.jar cglib-nodep-2.1_3.jar commons-codec-1.10.jar commons-exec-1.3.jar commons-io-2.4.jar commons-logging-1.2.jar gson-2.3.1.jar guava-19.0.jar hamcrest-core-1.3.jar hamcrest-library-1.3.jar httpclient-4.5.1.jar httpcore-4.4.3.jar httpmime-4.5.jar jcommander-1.48.jar jna-4.1.0.jar jna-platform-4.1.0.jar junit-4.12.jar netty-3.5.7.Final.jar phantomjsdriver-1.2.1.jar testng-6.9.9.jar selenium-java-2.53.1-srcs.jar selenium-java-2.53.1.jar

Running the application.

1.Import the project into STS workspace.
2.Import the Jars into classpath, from lib folder.
3.make sure that Safari Driver is installed on your safari browser
4.run as Java application
5.it connects to safari extension.(if you face any safari launching issue, please close the safari browser-let automatically launch from the interpreter)
6. Prompt for entering domain (lets say - http://wiprodigital.com) - Type ENTER Key


These resources are available in public GIT hub repository.
https://github.com/Yatheesh-Rai/Wipro-assignment