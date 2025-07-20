import java.util.concurrent.*;
class PrintChar1 implements Runnable {
    private char charToprint;
    private int times;

    public PrintChar1(char c, int t) {
        charToprint = c;
        times = t;
    }

    @Override
    public void run() {
        for (int i = 0; i < times; i++) {
            System.out.print(charToprint);
        }
    }
}
class PrintNum1 implements Runnable {
    private int lastnum;

    public PrintNum1(int n) {
        lastnum=n;
    }

    @Override
    public void run(){
        for(int i=1;i<=lastnum;i++){
            System.out.print(" "+i);
        }
    }
}
public class ExecutorDemo {
    public static void main(String[] args){
        ExecutorService executor = Executors.newFixedThreadPool(3);
        executor.execute(new PrintChar1('a', 100));
        executor.execute(new PrintChar1('b', 100));
        executor.execute(new PrintNum1(100));
        executor.shutdown();
    }
}
