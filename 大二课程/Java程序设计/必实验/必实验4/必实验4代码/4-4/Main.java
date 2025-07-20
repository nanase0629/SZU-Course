class Bridge{
    int ll=0;
    int rr=0;
    int f=0;
    int check_l=0;
    int check_r=0;
    int ff=1;
    String[]L={"E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11","E12","E13","E14","E15","E16","E17","E18","E19","E20","0"};
    String[]R={"W1","W2","W3","W4","W5","W6","W7","W8","W9","W10","W11","W12","W13","W14","W15","W16","W17","W18","W19","W20","0"};
    public synchronized void walk(String s) {
        for (int i = 0; i <=20; i++) {
            if (s == L[i]) {
                try {
                    System.out.print(L[i]+",");
                    ll++;
                    if(ll==20&&f==0){
                        f=1;
                        check_l=1;
                    }
                    notifyAll();
                    wait();
                } catch (InterruptedException ex) {
                }
            } else if (s == R[i]) {
                try {
                    System.out.print(R[i]+",");
                    rr++;
                    if(rr==20&&f==0){
                        f=1;
                        check_r=1;
                    }
                    notifyAll();
                    wait();
                } catch (InterruptedException ex) {
                }
            }

            notifyAll();
        }

        if(check_l==1&&ll==20&&rr==20&&ff==1) {
            System.out.println('\n'+"东边先到达");
            ff=0;
        }
        else if(check_r==1&&ll==20&&rr==20&&ff==1) {
            System.out.println('\n'+"西边先到达");
            ff=0;
        }
    }
}
class BridgeThread implements Runnable{
    Bridge bridge;
    String[]L={"E1","E2","E3","E4","E5","E6","E7","E8","E9","E10","E11","E12","E13","E14","E15","E16","E17","E18","E19","E20","0"};
    String[]R={"W1","W2","W3","W4","W5","W6","W7","W8","W9","W10","W11","W12","W13","W14","W15","W16","W17","W18","W19","W20","0"};
    public BridgeThread(){
        bridge=new Bridge();
    }
    @Override
    public void run() {
        for(int i=0;i<=20;i++) {
            if (Thread.currentThread().getName().equals(L[i])) {
                bridge.walk(L[i]);
            }
            else if (Thread.currentThread().getName().equals(R[i])) {
                bridge.walk(R[i]);
            }
        }
    }
}
public class Main {
    public static void main(String[] args) {
        BridgeThread bridgeThread=new BridgeThread();
        Thread[]L=new Thread[21];
        Thread[]R=new Thread[21];
        for(int i=0;i<=20;i++){
            L[i]=new Thread(bridgeThread);
            R[i]=new Thread(bridgeThread);
        }
        for(int i=0;i<=20;i++){
            L[i].setName("E"+i);
            R[i].setName("W"+i);
        }
        for(int i=0;i<=20;i++){
            L[i].start();
            R[i].start();
        }
    }
}