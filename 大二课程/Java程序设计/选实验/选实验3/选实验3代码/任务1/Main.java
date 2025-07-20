abstract class ball{
    public abstract void shape();
    public abstract void size();
    public abstract void show();
}

class ping_pong extends ball{
    String name = "乒乓球";
    @Override
    public void shape(){
        System.out.println("形状：球形");
    }
    @Override
    public void size(){
        System.out.println("尺寸：40mm");
    }
    @Override
    public void show(){
        System.out.println(name);
        shape();
        size();

    }
}

class badminton extends ball{
    String name = "羽毛球";
    public void shape(){
        System.out.println("形状：毛形");
    }
    public void size(){
        System.out.println("尺寸：60mm");
    }
    @Override
    public void show(){
        System.out.println(name);
        shape();
        size();

    }
}

class volleyball extends ball{
    String name = "排球";
    @Override
    public void shape(){
        System.out.println("形状：球形");
    }
    @Override
    public void size(){
        System.out.println("尺寸：65cm");
    }
    @Override
    public void show(){
        System.out.println(name);
        shape();
        size();

    }
}


public class Main {
    public static void main(String[] args) {
        ball p=new ping_pong();
        ball b =new badminton();
        ball v=new volleyball();
        p.show();
        b.show();
        v.show();
    }
}