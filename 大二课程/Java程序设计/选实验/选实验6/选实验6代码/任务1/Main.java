import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Random;

public class Main {
    public static void main(String[] args) {
        File file= new File("Exercisel_01.txt ");
        if(!file.exists()){
            try {
                file.createNewFile();
            }catch (IOException e){}

        }
        try(BufferedWriter writer=new BufferedWriter(new FileWriter(file))){
            Random random=new Random();
            for(int i=0;i<20;i++){
                writer.write(random.nextInt(100)+" ");
            }
            writer.newLine();
        }
       catch (IOException e){}

    }
}