import java.util.*;
import java.util.Random;

public class Main {
    public static void main(String[] args) {
        ArrayList<Integer>al=new ArrayList<>();
        LinkedList<Integer>ll=new LinkedList<>();
        HashSet<Integer>hs=new HashSet<>();
        LinkedHashSet<Integer>lh=new LinkedHashSet<>();
        TreeSet<Integer>ts=new TreeSet<>();
        for(int i=1;i<=50000;i++){
            al.add(i);
            ll.add(i);
            hs.add(i);
            lh.add(i);
            ts.add(i);
        }
        Random random=new Random();
        long start=System.currentTimeMillis();
        for(int i=1;i<=10000;i++){
            int r=random.nextInt(50000);
            al.contains(r);
        }
        long end=System.currentTimeMillis();

        System.out.println("ArrayList:"+(end-start));
        start=System.currentTimeMillis();
        for(int i=1;i<=10000;i++){
            int r=random.nextInt(50000);
            ll.contains(r);
        }
        end=System.currentTimeMillis();
        System.out.println("LinkedList:"+(end-start));

        start=System.currentTimeMillis();
        for(int i=1;i<=10000;i++) {
            int r = random.nextInt(50000);
            hs.contains(r);
        }
        end=System.currentTimeMillis();
        System.out.println("HashSet:" + (end - start));

        start=System.currentTimeMillis();
        for(int i=1;i<=10000;i++) {
            int r = random.nextInt(50000);
            lh.contains(r);
        }
        end=System.currentTimeMillis();
        System.out.println("LinkedHashSet:" + (end - start));

        start=System.currentTimeMillis();
        for(int i=1;i<=10000;i++) {
            int r = random.nextInt(50000);
            ts.contains(r);
        }
        end=System.currentTimeMillis();
        System.out.println("TreeSet:" + (end - start));
    }
}