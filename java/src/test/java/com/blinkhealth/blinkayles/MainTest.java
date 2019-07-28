package com.blinkhealth.blinkayles;

import static org.junit.Assert.assertEquals;
import java.io.IOException;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpDelete;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;
import org.junit.After;
import org.junit.Before;
import org.junit.Test;
import spark.Spark;

public class MainTest {
	
	@Before
    public void setup() {
        Main.main(null);
    }
    @After
    public void tearDown() throws Exception {
        Thread.sleep(1000);
        Spark.stop();
    }
    @Test
    public void test() throws IOException {

        CloseableHttpClient httpClient = HttpClients.custom().build();
        
        // Create Tournament with N players
        HttpPost httpPost = new HttpPost("http://0.0.0.0:4567/tournament");
        		 
        String requestBody = "{\"players\": [\"p1\", \"p2\", \"p3\"], \"pins\":10}";  
        StringEntity entity = new StringEntity(requestBody);
        httpPost.setEntity(entity);
        httpPost.setHeader("Accept", "application/json");
        httpPost.setHeader("Content-type", "application/json");
        		 
        CloseableHttpResponse response = httpClient.execute(httpPost);
        assertEquals(200, response.getStatusLine().getStatusCode());
        
        // Check if Tournament is running or ended
        HttpGet httpGet = new HttpGet("http://0.0.0.0:4567/tournament");
        CloseableHttpResponse response2 = httpClient.execute(httpGet);

        assertEquals(200, response2.getStatusLine().getStatusCode());
        assertEquals("{\"active\":[\"p1\",\"p2\",\"p3\"],\"losers\":[]}", EntityUtils.toString(response2.getEntity()));
        				 
        // Start Game
        HttpPost httpPost3 = new HttpPost("http://0.0.0.0:4567/game");
               		 
        String requestBody3 = "{\"player1\": \"p1\", \"player2\": \"p2\"}";
        StringEntity entity3 = new StringEntity(requestBody3);
        httpPost3.setEntity(entity3);
        httpPost3.setHeader("Accept", "application/json");
        httpPost3.setHeader("Content-type", "application/json");
        		        		 
        CloseableHttpResponse response3 = httpClient.execute(httpPost3);
        assertEquals(200, response3.getStatusLine().getStatusCode());
        assertEquals("Game started! The player who knocks down the last pin wins.  Players: p1 p2 Pins: 10", EntityUtils.toString(response3.getEntity()));
        
        // Move pins
        HttpPost httpPost4 = new HttpPost("http://0.0.0.0:4567/move/p1/1");
        CloseableHttpResponse response4 = httpClient.execute(httpPost4);
        assertEquals(response4.getStatusLine().getStatusCode(), 200);  
        System.out.println(EntityUtils.toString(response4.getEntity()));
        
        // Add player
        HttpPost httpPost5 = new HttpPost("http://0.0.0.0:4567/tournament/players/p4");
        CloseableHttpResponse response5 = httpClient.execute(httpPost5);
        assertEquals(response5.getStatusLine().getStatusCode(), 200); 
        assertEquals("Added player p4 to the tournament", EntityUtils.toString(response5.getEntity()));
        
        // Remove player
        HttpDelete httpDelete = new HttpDelete("http://0.0.0.0:4567/tournament/p3");
		CloseableHttpResponse response6 = httpClient.execute(httpDelete);
        assertEquals(response6.getStatusLine().getStatusCode(), 200);
        assertEquals("Removed player p3 from the tournament", EntityUtils.toString(response6.getEntity()));


    }
}

