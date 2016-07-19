package com.webcrawler.service;


import java.io.IOException;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.safari.SafariDriver;

public class XPATHGenerator {

	
	public static void main(String[] args) throws IOException, InterruptedException {
		WebDriver driver = new SafariDriver();
		System.out.println("Enter your domain: ");
		@SuppressWarnings("resource")
		Scanner scanner = new Scanner(System.in);
		String domain = scanner.nextLine();
		driver.get(domain);
		XPATHGenerator xpathDriverWrapper = new XPATHGenerator();
		WebElement htmlElement = driver.findElement(By.xpath("//body"));
		xpathDriverWrapper.generateXpaths(htmlElement, "//body", driver);
	}

	private void generateXpaths(WebElement currentEle,
			String currentXPATH, WebDriver driver) throws IOException, InterruptedException {
		Map<String, Integer> elemntCountMap = new HashMap<String, Integer>();

		List<WebElement> nextElements = null;
		if (currentXPATH.contains("@id")) {
			nextElements = driver
					.findElements(By.xpath(currentXPATH + "/*"));
		} else {
			nextElements = currentEle.findElements(By.xpath(currentXPATH
					+ "/*"));
		}
		for (Iterator<WebElement> iterator = nextElements.iterator(); iterator.hasNext();) {
			WebElement nextEle = (WebElement) iterator.next();
			String nextTag = nextEle.getTagName();
			String nextXPATH = buildXPATH(currentXPATH, elemntCountMap,
					nextTag, nextEle);
			generateXpaths(nextEle, nextXPATH, driver);
		}
	}


	private String buildXPATH(String currentXPATH,
			Map<String, Integer> elemntCountMap, String nextTag,
			WebElement nextElement) throws IOException, InterruptedException {
		String nextXPATH = null;
		String idAttr = nextElement.getAttribute("id");
		Integer indexval = elemntCountMap.get(nextTag);
		if (indexval == null) {
			indexval = 1;
		} else {
			indexval = indexval + 1;
		}
		elemntCountMap.put(nextTag, indexval);
		if (idAttr != null && idAttr.length() != 0) {
			nextXPATH = ".//*[@id='" + idAttr + "']";
		} else {
			nextXPATH = currentXPATH + "/" + nextTag + "[" + indexval + "]";
		}
		
		if (nextTag.equals("a") && nextXPATH.contains("/a") && nextElement.getAttribute("href")!= null && nextElement.getAttribute("href").length() != 0)  {
			String href = nextElement.getAttribute("href");
		    int pos = nextXPATH.indexOf("/a");
			String opt = nextXPATH.substring(0, pos + 3);
			nextXPATH = opt + "@href='" + href + "']";
			
			System.out.println("xpath " + nextXPATH);
			
		}
		return nextXPATH;
	}
}
